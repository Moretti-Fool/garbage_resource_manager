import secrets
import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Request
# from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from datetime import datetime, timedelta
from config import settings
from app.database import get_db
from app.models import User, Role, UserVerification, AuditLog
from app.schemas import UserCreate
from app.utils.authentication import get_password_hash
from celery_tasks.tasks import send_verification_email  # Ensure this is a valid Celery task


router = APIRouter(
    prefix="/register",
    tags=["Registration"]
)

@router.post("/")
async def register_user(
    request: Request,
    user: UserCreate,
    db: Session = Depends(get_db)
):
    raw_token = secrets.token_urlsafe(32)
    hashed_token = bcrypt.hashpw(raw_token.encode(), bcrypt.gensalt()).decode()

    async with db.begin():  # Transaction begins
        try:
            result = await db.execute(select(Role).where(Role.name == "USER"))
            default_role = result.scalar_one_or_none()

            if not default_role:
                new_role = Role(name="USER")
                db.add(new_role)
                await db.flush()  # Get ID of newly created role
                default_role = new_role  # Assign new role to user

            new_user = User(
                email=user.email,
                hashed_password=get_password_hash(user.password),
                role_id=default_role.id,  # Now guaranteed to exist
                is_verified=False
            )

            db.add(new_user)
            await db.flush()  # Ensure new_user gets an ID before committing

            verification_entry = UserVerification(
                token=hashed_token,
                user_id=new_user.id,
                expires_at=datetime.utcnow() + timedelta(minutes=settings.VERIFICATION_TOKEN_EXPIRE)
            )

            db.add(verification_entry)
            db.add(AuditLog(
                event="USER_REGISTERED",
                user_id=new_user.id,
                details=f"User {user.email} registered"
            ))

            # No need for db.commit() since db.begin() auto-commits if no error occurs.
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

    # Send verification email via Celery
    verification_link = f"http://127.0.0.1:8000/register/verify-email?token={raw_token}"
    send_verification_email.delay(user.email, verification_link)

    return {"message": "Registration successful. Check your email for verification."}


@router.get("/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    async with db.begin():
        result = await db.execute(
            select(UserVerification).where(
                UserVerification.expires_at > datetime.utcnow(),
                UserVerification.is_used == False
            )
        )
        verification_entries = result.scalars().all()

        # Find the valid token
        valid_entry = next(
            (entry for entry in verification_entries if bcrypt.checkpw(token.encode(), entry.token.encode())),
            None
        )

        if not valid_entry:
            db.add(AuditLog(
                event="VERIFICATION_FAILED",
                user_id=None,
                details="Invalid or expired token"
            ))
            await db.commit()
            raise HTTPException(status_code=400, detail="Invalid or expired token")

        user = await db.get(User, valid_entry.user_id)
        if not user:
            raise HTTPException(status_code=400, detail="User not found")

        # Update user verification status
        user.is_verified = True
        valid_entry.is_used = True

        db.add(AuditLog(
            event="USER_VERIFIED",
            user_id=user.id,
            details=f"User {user.email} verified"
        ))

        return {"message": "Email successfully verified."}
