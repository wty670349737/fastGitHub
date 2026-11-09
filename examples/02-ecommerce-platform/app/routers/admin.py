"""后台管理：仪表盘、商品 CRUD、订单状态。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from ..database import get_session
from ..deps import require_admin, verify_csrf
from ..models import Category, Order, Product, User
from ..templating import render

router = APIRouter(prefix="/admin")

ORDER_STATUSES = ["pending", "paid", "shipped", "completed", "cancelled"]


@router.get("")
def dashboard(
    request: Request,
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    stats = {
        "products": len(session.exec(select(Product)).all()),
        "active_products": len(
            session.exec(select(Product).where(Product.active == True)).all()  # noqa: E712
        ),
        "orders": len(session.exec(select(Order)).all()),
        "users": len(session.exec(select(User)).all()),
    }
    recent_orders = list(
        session.exec(select(Order).order_by(Order.id.desc()).limit(10)).all()
    )
    return render(
        request,
        "admin.html",
        stats=stats,
        recent_orders=recent_orders,
        statuses=ORDER_STATUSES,
    )


@router.get("/products")
def product_list(
    request: Request,
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    products = list(session.exec(select(Product).order_by(Product.id.desc())).all())
    return render(request, "admin_products.html", products=products)


@router.get("/products/new")
def product_new(
    request: Request,
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    categories = list(session.exec(select(Category)).all())
    return render(
        request, "admin_product_form.html", product=None, categories=categories
    )


@router.post("/products")
def product_create(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    price: float = Form(0.0),
    stock: int = Form(0),
    category_id: str = Form(""),
    active: bool = Form(False),
    csrf_token: str = Form(""),
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    verify_csrf(request, csrf_token)
    product = Product(
        name=name.strip(),
        description=description.strip(),
        price=max(0.0, price),
        stock=max(0, stock),
        category_id=_parse_category(category_id),
        active=active,
    )
    session.add(product)
    session.commit()
    return RedirectResponse("/admin/products", status_code=303)


@router.get("/products/{product_id}/edit")
def product_edit(
    product_id: int,
    request: Request,
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="商品不存在")
    categories = list(session.exec(select(Category)).all())
    return render(
        request,
        "admin_product_form.html",
        product=product,
        categories=categories,
    )


@router.post("/products/{product_id}")
def product_update(
    product_id: int,
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    price: float = Form(0.0),
    stock: int = Form(0),
    category_id: str = Form(""),
    active: bool = Form(False),
    csrf_token: str = Form(""),
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    verify_csrf(request, csrf_token)
    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="商品不存在")

    product.name = name.strip()
    product.description = description.strip()
    product.price = max(0.0, price)
    product.stock = max(0, stock)
    product.category_id = _parse_category(category_id)
    product.active = active
    session.add(product)
    session.commit()
    return RedirectResponse("/admin/products", status_code=303)


@router.post("/products/{product_id}/delete")
def product_delete(
    product_id: int,
    request: Request,
    csrf_token: str = Form(""),
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    verify_csrf(request, csrf_token)
    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="商品不存在")
    # 软删除：保留历史订单引用
    product.active = False
    session.add(product)
    session.commit()
    return RedirectResponse("/admin/products", status_code=303)


@router.post("/orders/{order_id}/status")
def order_status(
    order_id: int,
    request: Request,
    status: str = Form(...),
    csrf_token: str = Form(""),
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    verify_csrf(request, csrf_token)
    if status not in ORDER_STATUSES:
        raise HTTPException(status_code=400, detail="非法订单状态")
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="订单不存在")
    order.status = status
    session.add(order)
    session.commit()
    return RedirectResponse("/admin", status_code=303)


def _parse_category(value: str) -> int | None:
    try:
        return int(value) if value not in {"", "None", "none"} else None
    except ValueError:
        return None
