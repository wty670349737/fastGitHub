"""首页、商品搜索、商品详情与评价。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from ..database import get_session
from ..deps import get_current_user, verify_csrf
from ..models import Category, Product, Review, User
from ..templating import render

router = APIRouter()

PAGE_SIZE = 8


@router.get("/")
def index(
    request: Request,
    q: str = "",
    category: str = "",
    page: int = 1,
    session: Session = Depends(get_session),
    user: User | None = Depends(get_current_user),
):
    statement = select(Product).where(Product.active == True)  # noqa: E712
    if q:
        statement = statement.where(Product.name.contains(q))
    if category:
        selected = session.exec(
            select(Category).where(Category.slug == category)
        ).first()
        if selected is not None:
            statement = statement.where(Product.category_id == selected.id)

    statement = statement.order_by(Product.id.desc())
    all_products = list(session.exec(statement).all())
    total = len(all_products)

    page = max(1, page)
    start = (page - 1) * PAGE_SIZE
    products = all_products[start : start + PAGE_SIZE]
    pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)

    categories = list(session.exec(select(Category).order_by(Category.id)).all())
    return render(
        request,
        "index.html",
        products=products,
        categories=categories,
        q=q,
        category=category,
        page=page,
        pages=pages,
        total=total,
    )


@router.get("/product/{product_id}")
def product_detail(
    product_id: int,
    request: Request,
    session: Session = Depends(get_session),
    user: User | None = Depends(get_current_user),
):
    product = session.get(Product, product_id)
    if product is None or not product.active:
        raise HTTPException(status_code=404, detail="商品不存在")

    reviews = list(
        session.exec(
            select(Review)
            .where(Review.product_id == product_id)
            .order_by(Review.id.desc())
        ).all()
    )
    category = (
        session.get(Category, product.category_id) if product.category_id else None
    )
    return render(
        request,
        "product.html",
        product=product,
        reviews=reviews,
        category=category,
    )


@router.post("/product/{product_id}/review")
def add_review(
    product_id: int,
    request: Request,
    rating: int = Form(5),
    comment: str = Form(""),
    csrf_token: str = Form(""),
    session: Session = Depends(get_session),
    user: User | None = Depends(get_current_user),
):
    verify_csrf(request, csrf_token)
    if user is None:
        return RedirectResponse(f"/login?next=/product/{product_id}", status_code=303)

    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="商品不存在")

    review = Review(
        product_id=product_id,
        user_id=user.id,
        rating=min(5, max(1, rating)),
        comment=comment.strip()[:500],
    )
    session.add(review)
    session.commit()
    return RedirectResponse(f"/product/{product_id}", status_code=303)
