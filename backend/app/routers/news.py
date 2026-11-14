from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import News
from ..schemas import NewsCreate, NewsOut, NewsPage, NewsUpdate
from ..security import get_current_user

# 新闻列表对玩家前台公开只读；发布/编辑/删除需管理员登录
router = APIRouter(prefix="/api/news", tags=["新闻管理"])


def get_news_or_404(db: Session, news_id: int) -> News:
    news = db.get(News, news_id)
    if news is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="新闻不存在"
        )
    return news


@router.get("", response_model=NewsPage, summary="新闻列表（按发布时间倒序）")
def list_news(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> NewsPage:
    total = db.scalar(select(func.count()).select_from(News)) or 0
    items = (
        db.scalars(
            select(News)
            .order_by(News.published_at.desc(), News.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        .all()
    )
    return NewsPage(total=total, items=list(items))


@router.get("/{news_id}", response_model=NewsOut, summary="新闻详情")
def get_news(news_id: int, db: Session = Depends(get_db)) -> News:
    return get_news_or_404(db, news_id)


@router.post(
    "",
    response_model=NewsOut,
    status_code=status.HTTP_201_CREATED,
    summary="发布新闻",
    dependencies=[Depends(get_current_user)],
)
def create_news(payload: NewsCreate, db: Session = Depends(get_db)) -> News:
    data = payload.model_dump()
    data["published_at"] = data["published_at"] or datetime.now()
    news = News(**data)
    db.add(news)
    db.commit()
    db.refresh(news)
    return news


@router.put(
    "/{news_id}",
    response_model=NewsOut,
    summary="编辑新闻",
    dependencies=[Depends(get_current_user)],
)
def update_news(
    news_id: int, payload: NewsUpdate, db: Session = Depends(get_db)
) -> News:
    news = get_news_or_404(db, news_id)
    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="没有需要更新的字段"
        )
    for field, value in data.items():
        setattr(news, field, value)
    db.commit()
    db.refresh(news)
    return news


@router.delete(
    "/{news_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除新闻",
    dependencies=[Depends(get_current_user)],
)
def delete_news(news_id: int, db: Session = Depends(get_db)) -> None:
    news = get_news_or_404(db, news_id)
    db.delete(news)
    db.commit()
