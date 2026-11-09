from __future__ import annotations

from fastapi.testclient import TestClient


def get_csrf(client: TestClient) -> str:
    token = client.cookies.get("csrf_token")
    assert token, "CSRF cookie 未设置"
    return token


def login(
    client: TestClient,
    email: str = "demo@example.com",
    password: str = "demo123",
):
    client.get("/login")
    token = get_csrf(client)
    return client.post(
        "/login",
        data={
            "email": email,
            "password": password,
            "csrf_token": token,
            "next": "/",
        },
        follow_redirects=False,
    )


def test_health_and_products(client: TestClient) -> None:
    assert client.get("/api/health").json() == {"status": "ok"}
    products = client.get("/api/products").json()
    assert len(products) == 9


def test_home_page(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "精选好物" in response.text


def test_csrf_required(client: TestClient) -> None:
    # 没有先 GET 页面，拿不到 csrf cookie，直接 POST 应被拒绝
    response = client.post("/cart/add", data={"product_id": 1, "quantity": 1})
    assert response.status_code == 400


def test_register_cart_checkout(client: TestClient) -> None:
    client.get("/register")
    token = get_csrf(client)
    response = client.post(
        "/register",
        data={
            "email": "buyer@example.com",
            "name": "买家",
            "password": "secret123",
            "csrf_token": token,
        },
        follow_redirects=False,
    )
    assert response.status_code == 303

    token = get_csrf(client)
    response = client.post(
        "/cart/add",
        data={"product_id": 1, "quantity": 2, "csrf_token": token},
        follow_redirects=False,
    )
    assert response.status_code == 303

    cart = client.get("/cart")
    assert "iPhone 15" in cart.text

    token = get_csrf(client)
    response = client.post(
        "/checkout",
        data={"address": "北京市海淀区", "csrf_token": token},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert "/orders/" in response.headers["location"]

    orders = client.get("/orders")
    assert "pending" in orders.text

    products = client.get("/api/products").json()
    iphone = next(p for p in products if p["id"] == 1)
    assert iphone["stock"] == 18


def test_order_ownership(client: TestClient) -> None:
    client.get("/register")
    token = get_csrf(client)
    client.post(
        "/register",
        data={
            "email": "a@example.com",
            "password": "secret123",
            "csrf_token": token,
        },
    )

    token = get_csrf(client)
    client.post(
        "/cart/add",
        data={"product_id": 2, "quantity": 1, "csrf_token": token},
    )

    token = get_csrf(client)
    response = client.post(
        "/checkout",
        data={"address": "A 地址", "csrf_token": token},
        follow_redirects=False,
    )
    order_url = response.headers["location"]

    token = get_csrf(client)
    client.post("/logout", data={"csrf_token": token})

    client.get("/register")
    token = get_csrf(client)
    client.post(
        "/register",
        data={
            "email": "b@example.com",
            "password": "secret123",
            "csrf_token": token,
        },
    )

    # B 不能看 A 的订单
    assert client.get(order_url).status_code == 404


def test_admin_requires_admin(client: TestClient) -> None:
    assert client.get("/admin").status_code == 401

    login(client)
    assert client.get("/admin").status_code == 403

    client.cookies.clear()
    response = login(client, "admin@example.com", "admin123")
    assert response.status_code == 303
    assert client.get("/admin").status_code == 200


def test_api_pitch(client: TestClient) -> None:
    data = client.get("/api/products/1/pitch").json()
    assert data["product_id"] == 1
    assert "iPhone" in data["pitch"]
