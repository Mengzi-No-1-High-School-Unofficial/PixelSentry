"""认证 API 路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth import LoginRequest, LogoutResponse, RefreshRequest, TokenResponse
from app.services.auth_service import auth_service
from app.utils.jwt_helper import create_access_token, decode_token

router = APIRouter(prefix="/api/admin/auth", tags=["认证"])


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """管理员登录"""
    user = await auth_service.authenticate_user(db, request.username, request.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    tokens = await auth_service.create_tokens(user.id)

    return TokenResponse(success=True, **tokens)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshRequest):
    """刷新 Access Token"""
    try:
        # 验证 Refresh Token
        payload = decode_token(request.refreshToken, token_type="refresh")
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        # 创建新的 Access Token
        access_token = create_access_token({"sub": user_id})

        return TokenResponse(
            success=True,
            accessToken=access_token,
            expiresIn=3600,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"刷新 Token 失败: {str(e)}",
        )


@router.post("/logout", response_model=LogoutResponse)
async def logout():
    """登出（客户端需要清除 Token）"""
    # 注意：由于 JWT 是无状态的，服务端无法主动撤销
    # 实际的登出逻辑在客户端完成（清除存储的 Token）
    # 如果需要服务端黑名单，可以使用 Redis 存储已登出的 Token
    return LogoutResponse(success=True, message="登出成功")
