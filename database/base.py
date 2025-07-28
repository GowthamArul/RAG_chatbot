from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import AsyncGenerator
from configuration.config import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME

DATABASE_URL = f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"  # SQLite URL for async connections

# Create async engine
engine = create_async_engine(DATABASE_URL)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Description: get_db will make the session open and close once the API call is completed
    """
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()