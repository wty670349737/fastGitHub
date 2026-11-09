"""FastAPI 依赖：当前用户、权限、CSRF 校验。"""

from __future__ import annotations

import hmac

from fastapi import Depends, HTTPException, Request
from sqlmodel import Session

from .database import get_session
from .models import User
from .security import verify_session_token

SESSION_COOKIE = "session"
CSRF_COOKIE = "csrf_token"


def get_current_user(
    request: Request,
    session: Session = Depends(get_session),
) -> User | None:
    data = verify_session_token(request.cookies.get(SESSION_COOKIE))
    user = session.get(User, data["uid"]) if data else None
    request.state.user = user
    return user


def require_user(user: User | None = Depends(get_current_user)) -> User:
    if user is None:
        raise HTTPException(status_code=401, detail="请先登录")
    return user


def require_admin(user: User | None = Depends(get_current_user)) -> User:
    if user is None:
        raise HTTPException(status_code=401, detail="请先登录")
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user


def verify_csrf(request: Request, token: str) -> None:
    """双提交 Cookie 模式的 CSRF 校验。"""
    cookie = request.cookies.get(CSRF_COOKIE)
    if not cookie or not token or not hmac.compare_digest(cookie, token):
        raise HTTPException(status_code=400, detail="CSRF 校验失败，请刷新页面后重试")
