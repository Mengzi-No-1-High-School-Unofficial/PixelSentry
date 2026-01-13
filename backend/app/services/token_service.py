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
    async def retry_submission(
        db: AsyncSession, submission: Submission, force_full: bool = False
    ) -> None:
        """智能重试提交
        
        Args:
            db: 数据库会话
            submission: 提交记录
            force_full: 是否强制完整重试（忽略已有的 login_token）
        """
        try:
            # 更新状态为处理中
            submission.status = SubmissionStatus.PROCESSING
            submission.error_message = None
            await db.commit()

            # 如果已有 login_token 且不强制完整重试，只重试 AccessKey 获取（幂等）
            if submission.login_token and not force_full:
                logger.info(f"提交 {submission.id} 已有 login_token，只重试 AccessKey 获取")
                result = await camoufox_helper.get_access_key(submission.login_token)
            else:
                # 完整重试（非幂等，会生成新的 login_token）
                logger.info(f"提交 {submission.id} 执行完整重试")
                result = await camoufox_helper.get_full_token_flow(
                    submission.uid, submission.paste_id
                )

            if result["success"]:
                # 成功获取
                if "login_token" in result:
                    submission.login_token = result["login_token"]
                submission.access_key = result["access_key"]
                submission.status = SubmissionStatus.SUCCESS

                # 创建或更新 Access Key 记录
                access_key_record = AccessKey(
                    submission_id=submission.id,
                    access_key=result["access_key"],
                    is_valid=True,
                )
                db.add(access_key_record)

                logger.info(f"提交 {submission.id} 重试成功")
            else:
                # 失败
                submission.status = SubmissionStatus.FAILED
                submission.error_message = result.get("error", "Unknown error")
                logger.error(f"提交 {submission.id} 重试失败: {submission.error_message}")

            await db.commit()

        except Exception as e:
            logger.error(f"重试提交 {submission.id} 时发生异常: {e}")
            submission.status = SubmissionStatus.FAILED
            submission.error_message = str(e)
            await db.commit()

    @staticmethod
    async def create_and_process_submission(
        db: AsyncSession, uid: str | None, paste_id: str, submitter_name: str | None = None
    ) -> Submission:
        """创建提交并启动后台处理"""
        from app.database import AsyncSessionLocal
        
        # 如果 paste_id 是完整 URL，提取 ID
        if paste_id.startswith('http://') or paste_id.startswith('https://'):
            # 支持 https://www.luogu.com.cn/paste/xxx 或 https://www.luogu.com/paste/xxx
            if '/paste/' in paste_id:
                paste_id = paste_id.split('/paste/')[-1].split('?')[0].split('#')[0]
                logger.info(f"从 URL 提取剪贴板 ID: {paste_id}")
            else:
                raise ValueError("无效的剪贴板 URL 格式")
        
        username = None  # 用户名（从剪贴板解析）
        
        # 如果没有提供 UID，从剪贴板解析
        if not uid:
            logger.info(f"未提供 UID，尝试从剪贴板 {paste_id} 解析")
            result = await camoufox_helper.get_uid_from_paste_id(paste_id)
            
            if not result["success"]:
                error_msg = result.get("error", "未知错误")
                logger.error(f"无法从剪贴板解析 UID: {error_msg}")
                raise ValueError(f"无法获取 UID: {error_msg}")
            
            uid = result["uid"]
            username = result.get("username")
            logger.info(f"成功从剪贴板解析出 UID: {uid}, 用户名: {username}")
        
        # 创建提交记录
        submission = Submission(
            uid=uid, 
            paste_id=paste_id, 
            submitter_name=submitter_name,
            username=username,
            status=SubmissionStatus.PENDING
        )
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
