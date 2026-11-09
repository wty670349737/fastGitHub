"""轻量 JSON API：健康检查、商品列表、AI 文案。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import Product
from ..services.ai import generate_product_pitch

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/products")
def list_products(
    q: str = "",
    limit: int = 20,
    session: Session = Depends(get_session),
) -> list[dict]:
    statement = select(Product).where(Product.active == True)  # noqa: E712
    if q:
        statement = statement.where(Product.name.contains(q))
    statement = statement.order_by(Product.id.desc()).limit(max(1, min(100, limit)))
    products = session.exec(statement).all()
    return [
        {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "stock": product.stock,
        }
        for product in products
    ]


@router.get("/products/{product_id}/pitch")
def product_pitch(
    product_id: int,
    session: Session = Depends(get_session),
) -> dict:
    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="商品不存在")
    pitch = generate_product_pitch(product.name, product.description, product.price)
    return {"product_id": product.id, "pitch": pitch}
