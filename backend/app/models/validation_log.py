"""验证日志模型"""
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ValidationLog(Base):
    """验证日志表"""

    __tablename__ = "validation_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    access_key_id: Mapped[int] = mapped_column(
        ForeignKey("access_keys.id"), nullable=False, index=True
    )
    is_valid: Mapped[bool] = mapped_column(Boolean, nullable=False)
    response: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    # 关系
    access_key_record: Mapped["AccessKey"] = relationship("AccessKey", back_populates="validation_logs")
