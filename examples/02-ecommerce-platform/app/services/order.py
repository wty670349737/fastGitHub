"""下单业务：校验库存 -> 创建订单与订单项 -> 扣减库存 -> 清空购物车。"""

from __future__ import annotations

from sqlmodel import Session

from ..models import Order, OrderItem, User
from .cart import cart_total, get_cart_detail


def checkout(session: Session, user: User, address: str) -> Order:
    detail = get_cart_detail(session, user.id)
    if not detail:
        raise ValueError("购物车是空的")

    # 先整体校验库存，避免扣了一部分才发现不够
    for line in detail:
        product = line["product"]
        if product.stock < line["item"].quantity:
            raise ValueError(f"商品「{product.name}」库存不足")

    order = Order(user_id=user.id, total=cart_total(detail), address=address.strip())
    session.add(order)
    session.flush()  # 获取自增主键 order.id

    for line in detail:
        product = line["product"]
        item = line["item"]
        product.stock -= item.quantity
        session.add(product)
        session.add(
            OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                unit_price=product.price,
                quantity=item.quantity,
            )
        )
        session.delete(item)

    session.commit()
    session.refresh(order)
    return order
