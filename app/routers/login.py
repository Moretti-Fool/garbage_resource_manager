from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AuditLog, User
from app.utils.authentication import create_access_token, verify_password, get_current_user

router = APIRouter(
    tags=["Login"]
)

@router.post("/login")
async def login(
    response: Response,
    user_credentials: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_db)
):
    if not user_credentials.username or not user_credentials.password:
        raise HTTPException(status_code=422, detail="Missing required fields")

    async with db.begin():
        result = await db.execute(select(User).where(User.email == user_credentials.username))
        # result = db.query(User).filter(User.email == user_credentials.username).first()
        user = result.scalar_one_or_none()

        if not user or not verify_password(user_credentials.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        if not user.is_verified:
            raise HTTPException(status_code=400, detail="Not registered or verified")

        db.add(AuditLog(
            event="USER_LOGIN",
            user_id=user.id,
            details=f"User {user.email} Logged In"
        ))
        await db.commit()

    # Generate Access Token
    access_token = create_access_token(data={"user_id": user.id})

    # Set Cookies securely
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite="Strict")

    return {"message": "Login successful", "access_token": access_token}

@router.post("/logout")
async def logout(response: Response, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    response.delete_cookie("access_token")

    async with db.begin():
        db.add(AuditLog(
            event="USER_LOGOUT",
            user_id=current_user.id,
            details=f"User {current_user.email} Logged Out"
        ))
        await db.commit()

    return {"message": "Logged out successfully"}
