"""Token 获取服务"""
import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.access_key import AccessKey
from app.models.submission import Submission, SubmissionStatus
from app.utils.camoufox_helper import camoufox_helper

logger = logging.getLogger(__name__)


class TokenService:
    """Token 获取服务"""

    @staticmethod
    async def process_submission(db: AsyncSession, submission: Submission) -> None:
        """处理提交（异步后台任务）"""
        try:
            # 更新状态为处理中
            submission.status = SubmissionStatus.PROCESSING
            await db.commit()

            # 执行完整的 Token 获取流程
            result = await camoufox_helper.get_full_token_flow(
                submission.uid, submission.paste_id
            )

            if result["success"]:
                # 成功获取
                submission.login_token = result["login_token"]
                submission.access_key = result["access_key"]
                submission.status = SubmissionStatus.SUCCESS

                # 创建 Access Key 记录
                access_key_record = AccessKey(
                    submission_id=submission.id,
                    access_key=result["access_key"],
                    is_valid=True,
                )
                db.add(access_key_record)

                logger.info(f"提交 {submission.id} 处理成功")
            else:
                # 失败
                submission.status = SubmissionStatus.FAILED
                submission.error_message = result.get("error", "Unknown error")
                logger.error(f"提交 {submission.id} 处理失败: {submission.error_message}")

            await db.commit()

        except Exception as e:
            logger.error(f"处理提交 {submission.id} 时发生异常: {e}")
            submission.status = SubmissionStatus.FAILED
            submission.error_message = str(e)
            await db.commit()

    @staticmethod
    async def create_and_process_submission(
        db: AsyncSession, uid: str, paste_id: str
    ) -> Submission:
        """创建提交并启动后台处理"""
        from app.database import AsyncSessionLocal
        
        # 创建提交记录
        submission = Submission(uid=uid, paste_id=paste_id, status=SubmissionStatus.PENDING)
        db.add(submission)
        await db.commit()
        await db.refresh(submission)
        
        submission_id = submission.id

        # 启动后台任务处理（使用新的数据库会话）
        async def background_task():
            async with AsyncSessionLocal() as task_db:
                # 重新查询提交记录
                result = await task_db.execute(
                    select(Submission).where(Submission.id == submission_id)
                )
                task_submission = result.scalar_one()
                await TokenService.process_submission(task_db, task_submission)
        
        asyncio.create_task(background_task())

        return submission


# 全局实例
token_service = TokenService()
