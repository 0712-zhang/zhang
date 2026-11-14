from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserOut, UserPage, UserUpdate

router = APIRouter(prefix="/api/users", tags=["用户管理"])


def get_user_or_404(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在"
        )
    return user


def ensure_username_unique(
    db: Session, username: str, exclude_id: int | None = None
) -> None:
    stmt = select(User).where(User.username == username)
    if exclude_id is not None:
        stmt = stmt.where(User.id != exclude_id)
    if db.scalar(stmt) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在"
        )


@router.get("", response_model=UserPage, summary="用户列表（分页 + 关键字搜索）")
def list_users(
    keyword: str | None = Query(default=None, description="按用户名模糊搜索"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> UserPage:
    stmt = select(User)
    if keyword:
        stmt = stmt.where(User.username.like(f"%{keyword}%"))

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = (
        db.scalars(
            stmt.order_by(User.id).offset((page - 1) * page_size).limit(page_size)
        )
        .all()
    )
    return UserPage(total=total, items=list(items))


@router.get("/{user_id}", response_model=UserOut, summary="用户详情")
def get_user(user_id: int, db: Session = Depends(get_db)) -> User:
    return get_user_or_404(db, user_id)


@router.post(
    "",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="新增用户",
)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    ensure_username_unique(db, payload.username)
    user = User(**payload.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}", response_model=UserOut, summary="编辑用户")
def update_user(
    user_id: int, payload: UserUpdate, db: Session = Depends(get_db)
) -> User:
    user = get_user_or_404(db, user_id)
    data = payload.model_dump(exclude_unset=True)
    if "username" in data:
        ensure_username_unique(db, data["username"], exclude_id=user_id)
    for field, value in data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


@router.delete(
    "/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除用户"
)
def delete_user(user_id: int, db: Session = Depends(get_db)) -> None:
    user = get_user_or_404(db, user_id)
    db.delete(user)
    db.commit()
