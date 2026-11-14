from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import AppConfig
from ..schemas import ConfigOut, ConfigUpdate
from ..security import get_current_user

router = APIRouter(
    prefix="/api/config",
    tags=["系统配置"],
    dependencies=[Depends(get_current_user)],
)

DEFAULT_CONFIG = {
    "initial_capital": 1_000_000.0,
    "commission_rate": 0.03,
    "stamp_duty_rate": 0.1,
    "total_duration": 60,
    "round_duration": 5,
}


def get_or_create_config(db: Session) -> AppConfig:
    """配置为单行数据，不存在时按默认值创建。"""
    config = db.get(AppConfig, 1)
    if config is None:
        config = AppConfig(id=1, **DEFAULT_CONFIG)
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


@router.get("", response_model=ConfigOut, summary="读取系统配置")
def read_config(db: Session = Depends(get_db)) -> AppConfig:
    return get_or_create_config(db)


@router.put("", response_model=ConfigOut, summary="保存系统配置")
def update_config(
    payload: ConfigUpdate, db: Session = Depends(get_db)
) -> AppConfig:
    config = get_or_create_config(db)
    for field, value in payload.model_dump().items():
        setattr(config, field, value)
    db.commit()
    db.refresh(config)
    return config
