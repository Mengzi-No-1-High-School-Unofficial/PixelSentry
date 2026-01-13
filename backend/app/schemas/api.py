"""Pydantic 模式定义"""
from datetime import datetime

from pydantic import BaseModel, Field


# ============ 通用响应 ============
class BaseResponse(BaseModel):
    """基础响应模型"""

    success: bool
    message: str | None = None


# ============ 提交相关 ============
class SubmitRequest(BaseModel):
    """提交请求"""

    uid: str | None = Field(None, min_length=1, max_length=50, description="洛谷用户 ID（可选，如不提供将自动从剪贴板解析）")
    pasteId: str = Field(..., min_length=1, max_length=50, description="剪贴板 ID")
    submitterName: str | None = Field(None, min_length=1, max_length=100, description="提交人姓名（可选）")


class BatchSubmitRequest(BaseModel):
    """批量提交请求"""

    pasteIds: list[str] = Field(..., min_length=1, max_length=50, description="剪贴板 ID 列表")
    submitterName: str | None = Field(None, min_length=1, max_length=100, description="提交人姓名（可选）")


class SubmitResponse(BaseResponse):
    """提交响应"""

    submissionId: int | None = None


class SubmissionStatusResponse(BaseResponse):
    """提交状态响应"""

    data: dict | None = None


# ============ Access Key 相关 ============
class AccessKeyInfo(BaseModel):
    """Access Key 信息"""

    id: int
    accessKey: str
    isValid: bool
    lastValidatedAt: datetime | None
    validationCount: int
    createdAt: datetime
    submitterName: str | None = None
    username: str | None = None

    class Config:
        from_attributes = True


class AccessKeyListResponse(BaseResponse):
    """Access Key 列表响应"""

    data: list[AccessKeyInfo] = []


# ============ 统计相关 ============
class StatsData(BaseModel):
    """统计数据"""

    totalKeys: int
    validKeys: int
    totalSubmissions: int
    successRate: float


class StatsResponse(BaseResponse):
    """统计响应"""

    data: StatsData | None = None


# ============ 验证相关 ============
class ValidationResult(BaseModel):
    """验证结果"""

    isValid: bool
    paintToken: str | None = None


class ValidationResponse(BaseResponse):
    """验证响应"""

    data: ValidationResult | None = None
