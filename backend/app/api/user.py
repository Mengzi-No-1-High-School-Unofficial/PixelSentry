"""用户 API 路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.submission import Submission
from app.schemas.api import SubmissionStatusResponse, SubmitRequest, SubmitResponse
from app.services.token_service import token_service

router = APIRouter(prefix="/api", tags=["用户"])


@router.post("/submit", response_model=SubmitResponse)
async def submit_paste(request: SubmitRequest, db: AsyncSession = Depends(get_db)):
    """提交剪贴板信息"""
    try:
        submission = await token_service.create_and_process_submission(
            db, request.uid, request.pasteId
        )

        return SubmitResponse(
            success=True,
            submissionId=submission.id,
            message="提交成功，正在处理中",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提交失败: {str(e)}")


@router.get("/submission/{submission_id}", response_model=SubmissionStatusResponse)
async def get_submission_status(submission_id: int, db: AsyncSession = Depends(get_db)):
    """查询提交状态"""
    from sqlalchemy.orm import selectinload
    
    result = await db.execute(
        select(Submission)
        .options(selectinload(Submission.access_key_record))
        .where(Submission.id == submission_id)
    )
    submission = result.scalar_one_or_none()

    if not submission:
        raise HTTPException(status_code=404, detail="提交记录不存在")

    data = {
        "id": submission.id,
        "status": submission.status,
        "accessKey": submission.access_key,
        "isValid": submission.access_key_record.is_valid
        if submission.access_key_record
        else None,
        "errorMessage": submission.error_message,
        "createdAt": submission.created_at.isoformat(),
    }

    return SubmissionStatusResponse(success=True, data=data)
