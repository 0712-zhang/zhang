from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import LoginRequest, TokenResponse, UserOut
from ..security import create_access_token, get_current_user, verify_password

router = APIRouter(prefix="/api/auth", tags=["登录鉴权"])


@router.post("/login", response_model=TokenResponse, summary="管理员登录")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.username == payload.username))
    if (
        user is None
        or not user.password_hash
        or not verify_password(payload.password, user.password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="账号或密码错误"
        )
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="仅管理员可登录后台"
        )
    return TokenResponse(
        access_token=create_access_token(user),
        username=user.username,
        role=user.role,
    )


@router.get("/me", response_model=UserOut, summary="获取当前登录用户")
def read_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
