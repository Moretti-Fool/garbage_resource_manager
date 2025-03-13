import asyncio
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.database import SessionLocal
from sqlalchemy.future import select
from app.models import Role
from app.routers import uploads, admin, register, login
from app.services.cleanup import garbage_collector
from app.services.redis_client import get_redis


app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(register.router)
app.include_router(login.router)
app.include_router(uploads.router)
app.include_router(admin.router)


# Startup/shutdown events
@app.on_event("startup")
async def startup():
    async with SessionLocal() as db:
        for role in ["USER", "ADMIN"]:
            exists = await db.execute(select(Role).where(Role.name == role))
            if not exists.scalar_one_or_none():
                db.add(Role(name=role))
        await db.commit()
    # Connect to Redis
    app.state.redis = await get_redis()
    print("Connected to Redis and created roles")
    asyncio.create_task(garbage_collector())

@app.on_event("shutdown")
async def shutdown():
    await app.state.redis.close()
    print("Disconnected from Redis")