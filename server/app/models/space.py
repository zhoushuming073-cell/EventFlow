from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.mixins import TimestampMixin


class Space(Base, TimestampMixin):
    __tablename__ = "spaces"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    # 模板类型：baby / study / daily / pet / custom
    type: Mapped[str] = mapped_column(String(32), nullable=False, default="custom")
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    invite_code: Mapped[str] = mapped_column(
        String(16), unique=True, nullable=False, index=True
    )
