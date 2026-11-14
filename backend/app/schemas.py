from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Role = Literal["admin", "editor", "user"]
MatchStatus = Literal["pending", "ongoing", "finished"]


class UserBase(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    role: Role = Field(default="user", description="角色：admin / editor / user")


class UserCreate(UserBase):
    is_registered: bool = Field(default=False, description="报名状态")


class UserUpdate(BaseModel):
    """编辑时字段可选，只更新传入的字段。"""

    username: str | None = Field(default=None, min_length=2, max_length=50)
    role: Role | None = None
    is_registered: bool | None = None


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_registered: bool
    balance: float


class UserPage(BaseModel):
    total: int
    items: list[UserOut]


class GrantResult(BaseModel):
    updated: int
    amount: float


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


class ConfigBase(BaseModel):
    initial_capital: float = Field(..., gt=0, description="初始资金（元），必须为正数")
    commission_rate: float = Field(..., ge=0, le=100, description="手续费率（%）")
    stamp_duty_rate: float = Field(..., ge=0, le=100, description="印花税率（%）")
    total_duration: int = Field(..., ge=1, le=1440, description="比赛总时长（分钟）")
    round_duration: int = Field(..., ge=1, le=600, description="每回合时长（分钟）")

    @model_validator(mode="after")
    def check_duration_multiple(self) -> "ConfigBase":
        if self.total_duration % self.round_duration != 0:
            raise ValueError("比赛总时长必须是每回合时长的整数倍")
        return self


class ConfigUpdate(ConfigBase):
    pass


class ConfigOut(ConfigBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50, description="管理员账号")
    password: str = Field(..., min_length=1, max_length=128, description="密码")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: Role


class NewsCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="新闻标题")
    content: str = Field(..., min_length=1, description="新闻内容")
    published_at: datetime | None = Field(
        default=None, description="发布时间，不传则取当前时间"
    )


class NewsUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1)
    published_at: datetime | None = None


class NewsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    published_at: datetime


class NewsPage(BaseModel):
    total: int
    items: list[NewsOut]
