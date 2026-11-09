"""购物车业务逻辑。"""

from __future__ import annotations

from sqlmodel import Session, select

from ..models import CartItem, Product


def get_cart_items(session: Session, user_id: int) -> list[CartItem]:
    statement = (
        select(CartItem)
        .where(CartItem.user_id == user_id)
        .order_by(CartItem.id)
    )
    return list(session.exec(statement).all())


def get_cart_detail(session: Session, user_id: int) -> list[dict]:
    detail: list[dict] = []
    for item in get_cart_items(session, user_id):
        product = session.get(Product, item.product_id)
        if product is None:
            continue
        detail.append(
            {
                "item": item,
                "product": product,
                "subtotal": round(product.price * item.quantity, 2),
            }
        )
    return detail


def cart_total(detail: list[dict]) -> float:
    return round(sum(line["subtotal"] for line in detail), 2)


def add_to_cart(
    session: Session, user_id: int, product_id: int, quantity: int = 1
) -> CartItem:
    quantity = max(1, quantity)
    product = session.get(Product, product_id)
    if product is None or not product.active:
        raise ValueError("商品不存在或已下架")

    existing = session.exec(
        select(CartItem).where(
            CartItem.user_id == user_id, CartItem.product_id == product_id
        )
    ).first()

    if existing is not None:
        existing.quantity += quantity
        session.add(existing)
        item = existing
    else:
        item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        session.add(item)

    session.commit()
    session.refresh(item)
    return item


def update_quantity(
    session: Session, user_id: int, item_id: int, quantity: int
) -> None:
    item = session.get(CartItem, item_id)
    if item is None or item.user_id != user_id:
        raise ValueError("购物车条目不存在")
    if quantity <= 0:
        session.delete(item)
    else:
        item.quantity = quantity
        session.add(item)
    session.commit()


def remove_item(session: Session, user_id: int, item_id: int) -> None:
    item = session.get(CartItem, item_id)
    if item is None or item.user_id != user_id:
        raise ValueError("购物车条目不存在")
    session.delete(item)
    session.commit()
