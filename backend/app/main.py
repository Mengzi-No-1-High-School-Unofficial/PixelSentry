"""FastAPI 主应用"""
import logging

from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, auth, user
from app.config import settings
from app.database import AsyncSessionLocal, init_db
from app.services.auth_service import auth_service
from app.services.validation_service import validation_service

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 创建调度器
scheduler = AsyncIOScheduler()


async def scheduled_validation():
    """定时验证任务"""
    logger.info("开始定时验证所有 Access Key")
    async with AsyncSessionLocal() as db:
        try:
            result = await validation_service.validate_all_keys(db)
            logger.info(f"定时验证完成: {result}")
        except Exception as e:
            logger.error(f"定时验证失败: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("应用启动中...")

    # 初始化数据库
    await init_db()
    logger.info("数据库初始化完成")

    # 创建默认管理员账户
    async with AsyncSessionLocal() as db:
        await auth_service.get_or_create_admin(
            db, settings.ADMIN_USERNAME, settings.ADMIN_PASSWORD
        )

    # 启动定时任务
    scheduler.add_job(
        scheduled_validation,
        "interval",
        minutes=settings.VALIDATION_INTERVAL_MINUTES,
        id="validate_keys",
    )
    scheduler.start()
    logger.info(f"定时验证任务已启动，间隔 {settings.VALIDATION_INTERVAL_MINUTES} 分钟")

    yield

    # 关闭时执行
    logger.info("应用关闭中...")
    scheduler.shutdown()
    logger.info("调度器已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="PixelSentry Token 收集工具 API",
    lifespan=lifespan,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
