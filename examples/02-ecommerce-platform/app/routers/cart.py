"""购物车页面与操作。"""

from __future__ import annotations

from urllib.parse import quote

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from ..database import get_session
from ..deps import get_current_user, verify_csrf
from ..models import User
from ..services.cart import (
    add_to_cart,
    cart_total,
    get_cart_detail,
    remove_item,
    update_quantity,
)
from ..templating import render

router = APIRouter()


@router.get("/cart")
def cart_page(
    request: Request,
    session: Session = Depends(get_session),
    user: User | None = Depends(get_current_user),
):
    if user is None:
        return RedirectResponse("/login?next=/cart", status_code=303)
    detail = get_cart_detail(session, user.id)
    return render(request, "cart.html", detail=detail, total=cart_total(detail))


@router.post("/cart/add")
def cart_add(
    request: Request,
    product_id: int = Form(...),
    quantity: int = Form(1),
    csrf_token: str = Form(""),
    session: Session = Depends(get_session),
    user: User | None = Depends(get_current_user),
):
    verify_csrf(request, csrf_token)
    if user is None:
        return RedirectResponse(f"/login?next=/product/{product_id}", status_code=303)
    try:
        add_to_cart(session, user.id, product_id, quantity)
    except ValueError as exc:
        return RedirectResponse(
            f"/product/{product_id}?msg={quote(str(exc))}", status_code=303
        )
    return RedirectResponse("/cart", status_code=303)


@router.post("/cart/update")
def cart_update(
    request: Request,
    item_id: int = Form(...),
    quantity: int = Form(1),
    csrf_token: str = Form(""),
    session: Session = Depends(get_session),
    user: User | None = Depends(get_current_user),
):
    verify_csrf(request, csrf_token)
    if user is None:
        return RedirectResponse("/login?next=/cart", status_code=303)
    try:
        update_quantity(session, user.id, item_id, quantity)
    except ValueError as exc:
        return RedirectResponse(f"/cart?msg={quote(str(exc))}", status_code=303)
    return RedirectResponse("/cart", status_code=303)


@router.post("/cart/remove")
def cart_remove(
    request: Request,
    item_id: int = Form(...),
    csrf_token: str = Form(""),
    session: Session = Depends(get_session),
    user: User | None = Depends(get_current_user),
):
    verify_csrf(request, csrf_token)
    if user is None:
        return RedirectResponse("/login?next=/cart", status_code=303)
    try:
        remove_item(session, user.id, item_id)
    except ValueError as exc:
        return RedirectResponse(f"/cart?msg={quote(str(exc))}", status_code=303)
    return RedirectResponse("/cart", status_code=303)
