"""初始化演示数据：分类、商品、管理员与普通用户。幂等，可重复调用。"""

from __future__ import annotations

from sqlmodel import Session, select

from .config import get_settings
from .database import engine
from .models import Category, Product, User
from .security import hash_password

CATEGORIES = [
    ("手机数码", "digital"),
    ("家用电器", "appliance"),
    ("服饰鞋包", "fashion"),
    ("图书文娱", "books"),
]

PRODUCTS = [
    ("digital", "iPhone 15 128GB", "A16 芯片，4800 万像素主摄，支持 5G 双卡双待。", 4999.0, 20),
    ("digital", "小米 14 12GB+256GB", "徕卡光学镜头，骁龙 8 Gen3，120W 快充。", 3299.0, 35),
    ("digital", "Redmi K70", "第二代骁龙 8，2K 直屏，5000mAh 长续航。", 2199.0, 50),
    ("appliance", "空气炸锅 5L", "无油低脂，可视窗口，定时控温，适合家庭使用。", 299.0, 80),
    ("appliance", "扫地机器人 T10", "激光导航，自动集尘，扫拖一体。", 1599.0, 15),
    ("fashion", "纯棉基础 T 恤", "260g 重磅纯棉，不透不塌，多色可选。", 79.0, 200),
    ("fashion", "轻量通勤双肩包", "15.6 英寸电脑仓，防泼水面料，USB 充电口。", 159.0, 60),
    ("books", "Python 编程从入门到实践", "零基础友好的 Python 教材，配套大量练习。", 69.0, 100),
    ("books", "AI 应用开发实战", "从提示词到 RAG、Agent 的完整工程实践。", 89.0, 45),
]


def seed_all(session: Session | None = None) -> None:
    owns_session = session is None
    if owns_session:
        session = Session(engine)

    try:
        _seed_categories(session)
        _seed_products(session)
        _seed_users(session)
        session.commit()
    finally:
        if owns_session:
            session.close()


def _seed_categories(session: Session) -> None:
    existing = session.exec(select(Category)).first()
    if existing is not None:
        return
    for name, slug in CATEGORIES:
        session.add(Category(name=name, slug=slug))
    session.commit()


def _seed_products(session: Session) -> None:
    existing = session.exec(select(Product)).first()
    if existing is not None:
        return
    categories = {
        category.slug: category
        for category in session.exec(select(Category)).all()
    }
    for slug, name, description, price, stock in PRODUCTS:
        category = categories.get(slug)
        session.add(
            Product(
                category_id=category.id if category else None,
                name=name,
                description=description,
                price=price,
                stock=stock,
            )
        )
    session.commit()


def _seed_users(session: Session) -> None:
    settings = get_settings()

    admin = session.exec(select(User).where(User.email == settings.admin_email)).first()
    if admin is None:
        session.add(
            User(
                email=settings.admin_email,
                name="管理员",
                password_hash=hash_password(settings.admin_password),
                is_admin=True,
            )
        )

    demo_email = "demo@example.com"
    demo = session.exec(select(User).where(User.email == demo_email)).first()
    if demo is None:
        session.add(
            User(
                email=demo_email,
                name="演示用户",
                password_hash=hash_password("demo123"),
                is_admin=False,
            )
        )
    session.commit()
