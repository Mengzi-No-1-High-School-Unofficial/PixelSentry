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
    async def validate_access_key(access_key: str, uid: str = None) -> dict:
        """验证 Access Key 是否有效
        
        Args:
            access_key: Access Key
            uid: 用户 UID（如果不提供，将无法验证）
        """
        if not uid:
            logger.warning("验证 Access Key 时未提供 UID，无法验证")
            return {"is_valid": False, "paint_token": None, "response": {"error": "Missing UID"}}
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "https://paintboard.luogu.me/api/auth/gettoken",
                    json={"uid": int(uid), "access_key": access_key},
                    headers={"Content-Type": "application/json"}
                )
                data = response.json()['data']
                
                print(data)

                # 检查响应
                if "token" in data:
                    # 成功获取 token
                    return {"is_valid": True, "paint_token": data["token"], "response": data}
                elif "errorType" in data:
                    # 有错误
                    logger.warning(f"验证失败: {data['errorType']}")
                    return {"is_valid": False, "paint_token": None, "response": data}
                else:
                    # 未知响应
                    return {"is_valid": False, "paint_token": None, "response": data}

        except Exception as e:
            logger.error(f"验证 Access Key 失败: {e}")
            return {"is_valid": False, "paint_token": None, "response": {"error": str(e)}}

    @staticmethod
    async def validate_and_update(db: AsyncSession, key_record: AccessKey) -> bool:
        """验证并更新 Access Key 状态"""
        from sqlalchemy.orm import selectinload
        from app.models.submission import Submission
        
        # 获取关联的 submission 以获取 uid
        result = await db.execute(
            select(Submission)
            .where(Submission.id == key_record.submission_id)
        )
        submission = result.scalar_one_or_none()
        
        if not submission:
            logger.error(f"Access Key {key_record.id} 没有关联的 submission")
            return False
        
        # 验证
        validation_result = await ValidationService.validate_access_key(
            key_record.access_key, 
            submission.uid
        )

        # 更新记录
        key_record.is_valid = validation_result["is_valid"]
        key_record.last_validated_at = datetime.utcnow()
        key_record.validation_count += 1

        # 创建验证日志
        log = ValidationLog(
            access_key_id=key_record.id,
            is_valid=validation_result["is_valid"],
            response=validation_result["response"],
        )
        db.add(log)

        await db.commit()

        logger.info(
            f"验证 Access Key {key_record.access_key}: "
            f"{'有效' if validation_result['is_valid'] else '无效'}"
        )

        return validation_result["is_valid"]

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
