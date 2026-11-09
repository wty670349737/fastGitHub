"""注册、登录、退出。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from ..database import get_session
from ..deps import SESSION_COOKIE, get_current_user, verify_csrf
from ..models import User
from ..security import create_session_token, hash_password, verify_password
from ..templating import render

router = APIRouter()


def _safe_next(value: str | None) -> str:
    if value and value.startswith("/") and not value.startswith("//"):
        return value
    return "/"


def _set_session(response: RedirectResponse, user_id: int) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        create_session_token(user_id),
        httponly=True,
        samesite="lax",
        max_age=7 * 24 * 3600,
    )


@router.get("/register")
def register_page(request: Request, user: User | None = Depends(get_current_user)):
    if user is not None:
        return RedirectResponse("/", status_code=303)
    return render(request, "register.html")


@router.post("/register")
def register_submit(
    request: Request,
    email: str = Form(...),
    name: str = Form(""),
    password: str = Form(...),
    csrf_token: str = Form(""),
    session: Session = Depends(get_session),
):
    verify_csrf(request, csrf_token)
    email = email.strip().lower()
    name = name.strip()

    if len(password) < 6:
        return render(
            request, "register.html", error="密码至少 6 位", email=email, name=name
        )

    existing = session.exec(select(User).where(User.email == email)).first()
    if existing is not None:
        return render(
            request, "register.html", error="该邮箱已注册", email=email, name=name
        )

    user = User(
        email=email,
        name=name or email.split("@")[0],
        password_hash=hash_password(password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    response = RedirectResponse("/", status_code=303)
    _set_session(response, user.id)
    return response


@router.get("/login")
def login_page(
    request: Request,
    next: str = "/",
    user: User | None = Depends(get_current_user),
):
    if user is not None:
        return RedirectResponse("/", status_code=303)
    return render(request, "login.html", next=_safe_next(next))


@router.post("/login")
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    next: str = Form("/"),
    csrf_token: str = Form(""),
    session: Session = Depends(get_session),
):
    verify_csrf(request, csrf_token)
    email = email.strip().lower()

    user = session.exec(select(User).where(User.email == email)).first()
    if user is None or not verify_password(password, user.password_hash):
        return render(
            request,
            "login.html",
            error="邮箱或密码错误",
            email=email,
            next=_safe_next(next),
        )

    response = RedirectResponse(_safe_next(next), status_code=303)
    _set_session(response, user.id)
    return response


@router.post("/logout")
def logout(request: Request, csrf_token: str = Form("")):
    verify_csrf(request, csrf_token)
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie(SESSION_COOKIE)
    return response
