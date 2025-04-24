from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from decouple import config

from db.models import Base


# async
async_engine = create_async_engine(config('POSTGRES_URL'), echo=False)
async_session = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



# sync
sync_engine = create_engine(config('POSTGRES_URL_SYNC'))
sync_session = sessionmaker(bind=sync_engine, expire_on_commit=False)