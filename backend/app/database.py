"""数据库连接和会话管理"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """ORM 基类"""

    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话（依赖注入）"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """初始化数据库（创建所有表）"""
    import asyncio
    import logging
    
    # 确保所有模型都已被导入，以便 Base.metadata 能够通过 create_all 创建表
    from app.models.access_key import AccessKey  # noqa: F401
    from app.models.admin_user import AdminUser  # noqa: F401
    from app.models.submission import Submission  # noqa: F401
    from app.models.validation_log import ValidationLog  # noqa: F401

    logger = logging.getLogger(__name__)
    
    max_retries = 5
    retry_delay = 2
    
    for i in range(max_retries):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("数据库表创建成功")
            return
        except Exception as e:
            if i == max_retries - 1:
                logger.error(f"数据库初始化失败，重试次数耗尽: {e}")
                raise
            logger.warning(f"数据库连接失败，{retry_delay}秒后重试 ({i+1}/{max_retries}): {e}")
            await asyncio.sleep(retry_delay)
