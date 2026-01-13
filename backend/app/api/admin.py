"""管理员 API 路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.access_key import AccessKey
from app.models.admin_user import AdminUser
from app.models.submission import Submission, SubmissionStatus
from app.schemas.api import (
    AccessKeyInfo,
    AccessKeyListResponse,
    StatsData,
    StatsResponse,
    ValidationResponse,
    ValidationResult,
)
from app.services.validation_service import validation_service

router = APIRouter(prefix="/api/admin", tags=["管理员"])


@router.get("/keys", response_model=AccessKeyListResponse)
async def get_all_keys(
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user),
):
    """获取所有 Access Key"""
    result = await db.execute(select(AccessKey).order_by(AccessKey.created_at.desc()))
    keys = result.scalars().all()

    data = [
        AccessKeyInfo(
            id=key.id,
            accessKey=key.access_key,
            isValid=key.is_valid,
            lastValidatedAt=key.last_validated_at,
            validationCount=key.validation_count,
            createdAt=key.created_at,
        )
        for key in keys
    ]

    return AccessKeyListResponse(success=True, data=data)


@router.post("/validate/{key_id}", response_model=ValidationResponse)
async def validate_key(
    key_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user),
):
    """手动触发验证"""
    result = await db.execute(select(AccessKey).where(AccessKey.id == key_id))
    key_record = result.scalar_one_or_none()

    if not key_record:
        raise HTTPException(status_code=404, detail="Access Key 不存在")

    is_valid = await validation_service.validate_and_update(db, key_record)

    # 获取验证结果
    validation_result = await validation_service.validate_access_key(key_record.access_key)

    return ValidationResponse(
        success=True,
        data=ValidationResult(
            isValid=is_valid,
            paintToken=validation_result.get("paint_token"),
        ),
    )


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user),
):
    """获取统计信息"""
    # 总 Key 数量
    total_keys_result = await db.execute(select(func.count(AccessKey.id)))
    total_keys = total_keys_result.scalar_one()

    # 有效 Key 数量
    valid_keys_result = await db.execute(
        select(func.count(AccessKey.id)).where(AccessKey.is_valid == True)
    )
    valid_keys = valid_keys_result.scalar_one()

    # 总提交数量
    total_submissions_result = await db.execute(select(func.count(Submission.id)))
    total_submissions = total_submissions_result.scalar_one()

    # 成功提交数量
    success_submissions_result = await db.execute(
        select(func.count(Submission.id)).where(Submission.status == SubmissionStatus.SUCCESS)
    )
    success_submissions = success_submissions_result.scalar_one()

    # 成功率
    success_rate = (
        success_submissions / total_submissions if total_submissions > 0 else 0.0
    )

    data = StatsData(
        totalKeys=total_keys,
        validKeys=valid_keys,
        totalSubmissions=total_submissions,
        successRate=round(success_rate, 2),
    )

    return StatsResponse(success=True, data=data)
