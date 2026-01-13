"""认证相关模式"""
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """登录请求"""

    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """Token 响应"""

    success: bool
    accessToken: str | None = None
    refreshToken: str | None = None
    expiresIn: int | None = None
    message: str | None = None


class RefreshRequest(BaseModel):
    """刷新 Token 请求"""

    refreshToken: str


class LogoutResponse(BaseModel):
    """登出响应"""

    success: bool
    message: str
