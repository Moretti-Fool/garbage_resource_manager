from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal
from app.models import Resource, User


async def get_resource_filename(session: AsyncSession, resource_id: str) -> str | None:
    result = await session.execute(select(Resource.filename).where(Resource.id == resource_id))
    return result.scalar_one_or_none()


async def get_resource_email(session: AsyncSession, resource_id: str) -> str | None:

    result = await session.execute(select(Resource.user_id).where(Resource.id == resource_id))
    resource = result.scalar()
    users = await session.execute(select(User.email).where(User.id == resource))
    user = users.scalar()
    return user

