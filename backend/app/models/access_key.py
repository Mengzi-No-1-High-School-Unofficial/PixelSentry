"""Access Key 模型"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AccessKey(Base):
    """Access Key 管理表"""

    __tablename__ = "access_keys"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    submission_id: Mapped[int] = mapped_column(
        ForeignKey("submissions.id"), nullable=False, unique=True, index=True
    )
    access_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    paint_token: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="绘画 Token (UUID 格式)")
    paint_token_obtained_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="Paint Token 获取时间")
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    last_validated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    validation_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    submitter_name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="提交人")
    username: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="洛谷用户名")

    # 关系
    submission: Mapped["Submission"] = relationship("Submission", back_populates="access_key_record")
    validation_logs: Mapped[list["ValidationLog"]] = relationship(
        "ValidationLog", back_populates="access_key_record", cascade="all, delete-orphan"
    )
