"""数据模型：用户、分类、商品、购物车、订单、订单项、评价。"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    name: str = ""
    password_hash: str
    is_admin: bool = False
    created_at: datetime = Field(default_factory=utcnow)


class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    slug: str = Field(index=True, unique=True)


class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: int | None = Field(default=None, primary_key=True)
    category_id: int | None = Field(
        default=None, index=True, foreign_key="categories.id"
    )
    name: str = Field(index=True)
    description: str = ""
    price: float = 0.0
    stock: int = 0
    image_url: str = ""
    active: bool = True
    created_at: datetime = Field(default_factory=utcnow)


class CartItem(SQLModel, table=True):
    __tablename__ = "cart_items"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="users.id")
    product_id: int = Field(index=True, foreign_key="products.id")
    quantity: int = 1
    created_at: datetime = Field(default_factory=utcnow)


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="users.id")
    status: str = "pending"
    total: float = 0.0
    address: str = ""
    created_at: datetime = Field(default_factory=utcnow)


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"

    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(index=True, foreign_key="orders.id")
    product_id: int
    product_name: str
    unit_price: float
    quantity: int


class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    id: int | None = Field(default=None, primary_key=True)
    product_id: int = Field(index=True, foreign_key="products.id")
    user_id: int = Field(index=True, foreign_key="users.id")
    rating: int = 5
    comment: str = ""
    created_at: datetime = Field(default_factory=utcnow)
