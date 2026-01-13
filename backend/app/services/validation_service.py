"""验证服务"""
import logging
from datetime import datetime

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.access_key import AccessKey
from app.models.validation_log import ValidationLog

logger = logging.getLogger(__name__)


class ValidationService:
    """Access Key 验证服务"""

    @staticmethod
    async def validate_access_key(access_key: str) -> dict:
        """验证 Access Key 是否有效"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"https://www.luogu.com.cn/paintboard/gettoken?token={access_key}"
                )
                data = response.json()

                is_valid = data.get("success", False)
                paint_token = data.get("token") if is_valid else None

                return {"is_valid": is_valid, "paint_token": paint_token, "response": data}

        except Exception as e:
            logger.error(f"验证 Access Key 失败: {e}")
            return {"is_valid": False, "paint_token": None, "response": {"error": str(e)}}

    @staticmethod
    async def validate_and_update(db: AsyncSession, key_record: AccessKey) -> bool:
        """验证并更新 Access Key 状态"""
        result = await ValidationService.validate_access_key(key_record.access_key)

        # 更新记录
        key_record.is_valid = result["is_valid"]
        key_record.last_validated_at = datetime.utcnow()
        key_record.validation_count += 1

        # 创建验证日志
        log = ValidationLog(
            access_key_id=key_record.id,
            is_valid=result["is_valid"],
            response=result["response"],
        )
        db.add(log)

        await db.commit()

        logger.info(
            f"验证 Access Key {key_record.access_key}: "
            f"{'有效' if result['is_valid'] else '无效'}"
        )

        return result["is_valid"]

    @staticmethod
    async def validate_all_keys(db: AsyncSession) -> dict[str, int]:
        """验证所有 Access Key"""
        result = await db.execute(select(AccessKey))
        keys = result.scalars().all()

        total = len(keys)
        valid_count = 0

        for key_record in keys:
            is_valid = await ValidationService.validate_and_update(db, key_record)
            if is_valid:
                valid_count += 1

        logger.info(f"验证完成: {valid_count}/{total} 个 Key 有效")

        return {"total": total, "valid": valid_count, "invalid": total - valid_count}


# 全局实例
validation_service = ValidationService()
