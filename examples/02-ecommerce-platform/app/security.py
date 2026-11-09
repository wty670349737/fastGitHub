"""密码哈希与登录会话令牌。

- 密码：PBKDF2-HMAC-SHA256 + 随机盐，绝不存明文。
- 会话：body.signature 的 HMAC-SHA256 签名令牌，放在 HttpOnly Cookie 中。
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time

from .config import get_settings

PBKDF2_ITERATIONS = 200_000
SESSION_TTL = 7 * 24 * 3600


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64decode(text: str) -> bytes:
    padding = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + padding)


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), PBKDF2_ITERATIONS
    ).hex()
    return f"{salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, expected = stored.split("$", 1)
    except ValueError:
        return False
    actual = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), PBKDF2_ITERATIONS
    ).hex()
    return hmac.compare_digest(actual, expected)


def _sign(body: str) -> str:
    secret = get_settings().secret_key.encode("utf-8")
    signature = hmac.new(secret, body.encode("utf-8"), hashlib.sha256).digest()
    return _b64encode(signature)


def create_session_token(user_id: int) -> str:
    payload = {"uid": user_id, "exp": int(time.time()) + SESSION_TTL}
    body = _b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    return f"{body}.{_sign(body)}"


def verify_session_token(token: str | None) -> dict | None:
    if not token or "." not in token:
        return None
    body, signature = token.rsplit(".", 1)
    if not hmac.compare_digest(signature.encode("ascii"), _sign(body).encode("ascii")):
        return None
    try:
        payload = json.loads(_b64decode(body))
    except (ValueError, json.JSONDecodeError):
        return None
    if int(payload.get("exp", 0)) < int(time.time()):
        return None
    user_id = payload.get("uid")
    return {"uid": int(user_id)} if user_id is not None else None
