from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")
    # 报名状态
    is_registered: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    # 账户当前资金
    balance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    # 登录密码哈希（pbkdf2_sha256），空字符串表示未设置密码、不能登录
    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False, default=""
    )


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


class News(Base):
    """新闻公告。"""

    __tablename__ = "news"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    content: Mapped[str] = mapped_column(String, nullable=False)
    published_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now, index=True
    )


class AppConfig(Base):
    """系统与赛制配置，全局仅一行（id=1）。"""

    __tablename__ = "app_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    initial_capital: Mapped[float] = mapped_column(
        Float, nullable=False, default=1_000_000
    )
    # 费率单位为百分比，例如 0.03 表示 0.03%
    commission_rate: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.03
    )
    stamp_duty_rate: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.1
    )
    total_duration: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    round_duration: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
