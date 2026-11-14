from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text

from .database import Base, SessionLocal, engine
from .models import User
from .routers import auth, config, matches, news, users
from .security import hash_password

# 初始管理员密码，首次启动写入数据库；登录后请尽快修改
DEFAULT_ADMIN_PASSWORD = "admin123"


def migrate_schema() -> None:
    """为已存在的 SQLite 库补充新增列（create_all 不会改老表）。"""
    with engine.begin() as conn:
        columns = {row[1] for row in conn.execute(text("PRAGMA table_info(users)"))}
        if "is_registered" not in columns:
            conn.execute(
                text(
                    "ALTER TABLE users ADD COLUMN is_registered "
                    "BOOLEAN NOT NULL DEFAULT 0"
                )
            )
        if "balance" not in columns:
            conn.execute(
                text("ALTER TABLE users ADD COLUMN balance FLOAT NOT NULL DEFAULT 0")
            )
        if "password_hash" not in columns:
            conn.execute(
                text(
                    "ALTER TABLE users ADD COLUMN password_hash "
                    "VARCHAR(255) NOT NULL DEFAULT ''"
                )
            )


def seed_data() -> None:
    """首次启动时写入几条演示数据，并保证管理员有初始密码。"""
    with SessionLocal() as db:
        if db.query(User).count() == 0:
            db.add_all(
                [
                    User(username="admin", role="admin"),
                    User(username="editor", role="editor"),
                    User(username="zhangsan", role="user"),
                ]
            )
            db.commit()

        admin = db.scalar(select(User).where(User.username == "admin"))
        if admin is None:
            # 已有数据但没有管理员账号时补建默认管理员
            admin = User(
                username="admin",
                role="admin",
                password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
            )
            db.add(admin)
            db.commit()
        elif not admin.password_hash:
            admin.password_hash = hash_password(DEFAULT_ADMIN_PASSWORD)
            db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    migrate_schema()
    seed_data()
    yield


app = FastAPI(title="管理员后台 API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(matches.router)
app.include_router(config.router)
app.include_router(news.router)


@app.get("/api/health", tags=["系统"], summary="健康检查")
def health() -> dict[str, str]:
    return {"status": "ok"}
