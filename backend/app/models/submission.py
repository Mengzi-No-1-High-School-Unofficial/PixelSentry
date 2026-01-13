"""提交记录模型"""
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SubmissionStatus(str, Enum):
    """提交状态枚举"""

    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"


class Submission(Base):
    """提交记录表"""

    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    uid: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    paste_id: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[SubmissionStatus] = mapped_column(
        String(20), default=SubmissionStatus.PENDING, nullable=False, index=True
    )
    login_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    access_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # 关系
    access_key_record: Mapped["AccessKey"] = relationship(
        "AccessKey", back_populates="submission", uselist=False
    )
