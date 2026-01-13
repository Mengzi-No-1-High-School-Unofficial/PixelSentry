"""应用配置模块"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://pixelsentry:password@localhost:5432/pixelsentry"

    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT 配置
    JWT_SECRET_KEY: str = "your-secret-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 管理员账户
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"

    # 应用配置
    APP_NAME: str = "PixelSentry"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # CORS 配置
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        """获取 CORS 允许的源列表"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # 验证配置
    VALIDATION_INTERVAL_MINUTES: int = 5

    # Camoufox 配置
    CAMOUFOX_HEADLESS: bool = True
    CAMOUFOX_TIMEOUT: int = 30000


# 全局配置实例
settings = Settings()
