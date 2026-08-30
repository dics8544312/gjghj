"""
Настройка подключения к базе данных
SQLAlchemy async engine и сессии
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from config import settings


# Создаем асинхронный движок для PostgreSQL
engine = create_async_engine(
    settings.database_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Создаем фабрику сессий
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Базовый класс для моделей
class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """
    Получение сессии базы данных
    Используется как dependency
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Инициализация базы данных
    Создает все таблицы
    """
    # Импортируем все модели чтобы они зарегистрировались в Base.metadata
    from models import User, AccessCode, Task, Progress, ParentChild  # noqa
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """
    Закрытие соединения с базой данных
    """
    await engine.dispose()
