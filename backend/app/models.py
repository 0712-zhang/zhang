from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # pending=未开始, ongoing=进行中, finished=已结束
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", index=True
    )
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    current_round: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
