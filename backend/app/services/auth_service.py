"""认证服务"""
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin_user import AdminUser
from app.utils.jwt_helper import create_access_token, create_refresh_token
from app.utils.security import hash_password, verify_password

logger = logging.getLogger(__name__)


class AuthService:
    """认证服务"""

    @staticmethod
    async def authenticate_user(
        db: AsyncSession, username: str, password: str
    ) -> AdminUser | None:
        """验证用户凭据"""
        result = await db.execute(select(AdminUser).where(AdminUser.username == username))
        user = result.scalar_one_or_none()

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    @staticmethod
    async def create_tokens(user_id: int) -> dict[str, str | int]:
        """创建访问和刷新 Token"""
        access_token = create_access_token({"sub": str(user_id)})
        refresh_token = create_refresh_token({"sub": str(user_id)})

        return {
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "expiresIn": 3600,  # 1 小时
        }

    @staticmethod
    async def create_admin_user(db: AsyncSession, username: str, password: str) -> AdminUser:
        """创建管理员用户"""
        hashed_password = hash_password(password)
        user = AdminUser(username=username, hashed_password=hashed_password)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"创建管理员用户: {username}")
        return user

    @staticmethod
    async def get_or_create_admin(db: AsyncSession, username: str, password: str) -> AdminUser:
        """获取或创建管理员用户"""
        result = await db.execute(select(AdminUser).where(AdminUser.username == username))
        user = result.scalar_one_or_none()

        if not user:
            user = await AuthService.create_admin_user(db, username, password)

        return user


# 全局实例
auth_service = AuthService()
