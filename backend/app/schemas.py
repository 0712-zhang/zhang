from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Role = Literal["admin", "editor", "user"]
MatchStatus = Literal["pending", "ongoing", "finished"]


class UserBase(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    role: Role = Field(default="user", description="角色：admin / editor / user")


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    """编辑时字段可选，只更新传入的字段。"""

    username: str | None = Field(default=None, min_length=2, max_length=50)
    role: Role | None = None


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class UserPage(BaseModel):
    total: int
    items: list[UserOut]


class MatchBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="比赛名称")
    start_time: datetime = Field(..., description="开始时间")
    current_round: int = Field(default=1, ge=1, description="当前轮次")


class MatchCreate(MatchBase):
    """新建比赛，状态由后端固定为 pending（未开始）。"""


class MatchUpdate(BaseModel):
    """编辑 / 状态变更，只更新传入的字段。"""

    name: str | None = Field(default=None, min_length=2, max_length=100)
    start_time: datetime | None = None
    current_round: int | None = Field(default=None, ge=1)
    status: MatchStatus | None = None


class MatchOut(MatchBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: MatchStatus


class MatchStatusUpdate(BaseModel):
    """管理员手动切换比赛状态，不接受客户端自动推算。"""

    status: MatchStatus


class MatchPage(BaseModel):
    total: int
    items: list[MatchOut]
