"""下单与订单查询。"""

from __future__ import annotations

from urllib.parse import quote

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from ..database import get_session
from ..deps import get_current_user, verify_csrf
from ..models import Order, OrderItem, User
from ..services.order import checkout
from ..templating import render

router = APIRouter()


@router.post("/checkout")
def checkout_submit(
    request: Request,
    address: str = Form(...),
    csrf_token: str = Form(""),
    session: Session = Depends(get_session),
    user: User | None = Depends(get_current_user),
):
    verify_csrf(request, csrf_token)
    if user is None:
        return RedirectResponse("/login?next=/cart", status_code=303)
    if not address.strip():
        return RedirectResponse("/cart?msg=请填写收货地址", status_code=303)
    try:
        order = checkout(session, user, address)
    except ValueError as exc:
        session.rollback()
        return RedirectResponse(f"/cart?msg={quote(str(exc))}", status_code=303)
    return RedirectResponse(f"/orders/{order.id}", status_code=303)


@router.get("/orders")
def orders_page(
    request: Request,
    session: Session = Depends(get_session),
    user: User | None = Depends(get_current_user),
):
    if user is None:
        return RedirectResponse("/login?next=/orders", status_code=303)
    orders = list(
        session.exec(
            select(Order).where(Order.user_id == user.id).order_by(Order.id.desc())
        ).all()
    )
    return render(request, "orders.html", orders=orders)


@router.get("/orders/{order_id}")
def order_detail(
    order_id: int,
    request: Request,
    session: Session = Depends(get_session),
    user: User | None = Depends(get_current_user),
):
    if user is None:
        return RedirectResponse(f"/login?next=/orders/{order_id}", status_code=303)
    order = session.get(Order, order_id)
    if order is None or order.user_id != user.id:
        raise HTTPException(status_code=404, detail="订单不存在")
    items = list(
        session.exec(
            select(OrderItem).where(OrderItem.order_id == order.id)
        ).all()
    )
    return render(request, "order_detail.html", order=order, items=items)
