import csv
import io
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Match, User
from ..schemas import (
    MatchCreate,
    MatchOut,
    MatchPage,
    MatchStatusUpdate,
    MatchUpdate,
)
from .config import get_or_create_config
from ..security import get_current_user

router = APIRouter(
    prefix="/api/matches",
    tags=["比赛管理"],
    dependencies=[Depends(get_current_user)],
)

STATUS_LABELS = {"pending": "未开始", "ongoing": "进行中", "finished": "已结束"}


def get_match_or_404(db: Session, match_id: int) -> Match:
    match = db.get(Match, match_id)
    if match is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="比赛不存在"
        )
    return match


@router.get("", response_model=MatchPage, summary="比赛列表（分页）")
def list_matches(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> MatchPage:
    total = db.scalar(select(func.count()).select_from(Match)) or 0
    items = (
        db.scalars(
            select(Match)
            .order_by(Match.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        .all()
    )
    return MatchPage(total=total, items=list(items))


@router.get("/{match_id}/export", summary="导出比赛成绩 CSV")
def export_match_results(
    match_id: int, db: Session = Depends(get_db)
) -> StreamingResponse:
    match = get_match_or_404(db, match_id)
    config = get_or_create_config(db)
    users = db.scalars(select(User).order_by(User.id)).all()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "比赛ID",
            "比赛名称",
            "比赛状态",
            "用户ID",
            "用户名",
            "报名状态",
            "初始资金",
            "当前资金",
            "收益",
        ]
    )
    for user in users:
        # 未发放资金（balance 为 0）的用户收益留空
        profit = (
            round(user.balance - config.initial_capital, 2) if user.balance else ""
        )
        writer.writerow(
            [
                match.id,
                match.name,
                STATUS_LABELS.get(match.status, match.status),
                user.id,
                user.username,
                "已报名" if user.is_registered else "未报名",
                f"{config.initial_capital:.2f}",
                f"{user.balance:.2f}",
                profit,
            ]
        )

    # \ufeff 保证 Excel 打开中文不乱码
    content = "\ufeff" + buffer.getvalue()
    filename = f"match_{match.id}_result.csv"
    return StreamingResponse(
        iter([content]),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"
        },
    )


@router.get("/{match_id}", response_model=MatchOut, summary="比赛详情")
def get_match(match_id: int, db: Session = Depends(get_db)) -> Match:
    return get_match_or_404(db, match_id)


@router.post(
    "",
    response_model=MatchOut,
    status_code=status.HTTP_201_CREATED,
    summary="新建比赛",
)
def create_match(payload: MatchCreate, db: Session = Depends(get_db)) -> Match:
    # 新建比赛一律为“未开始”，不接受前端传入状态
    match = Match(**payload.model_dump(), status="pending")
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


@router.put(
    "/{match_id}/status", response_model=MatchOut, summary="更新比赛状态（手动）"
)
def update_match_status(
    match_id: int, payload: MatchStatusUpdate, db: Session = Depends(get_db)
) -> Match:
    """状态完全由管理员手动指定：未开始 / 进行中 / 已结束。"""
    match = get_match_or_404(db, match_id)
    match.status = payload.status
    db.commit()
    db.refresh(match)
    return match


@router.put("/{match_id}", response_model=MatchOut, summary="编辑比赛 / 变更状态")
def update_match(
    match_id: int, payload: MatchUpdate, db: Session = Depends(get_db)
) -> Match:
    match = get_match_or_404(db, match_id)
    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="没有需要更新的字段"
        )
    for field, value in data.items():
        setattr(match, field, value)
    db.commit()
    db.refresh(match)
    return match


@router.delete(
    "/{match_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除比赛"
)
def delete_match(match_id: int, db: Session = Depends(get_db)) -> None:
    match = get_match_or_404(db, match_id)
    db.delete(match)
    db.commit()
