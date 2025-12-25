from __future__ import annotations

import time
import uuid
from dataclasses import dataclass

import jwt
from django.conf import settings


@dataclass(frozen=True)
class JwtUserPayload:
    sub: str
    username: str
    role: str


class JwtError(Exception):
    pass


def _now() -> int:
    return int(time.time())


def sign_access(payload: JwtUserPayload) -> str:
    now = _now()
    body = {
        "sub": payload.sub,
        "username": payload.username,
        "role": payload.role,
        "type": "access",
        "iat": now,
        "exp": now + settings.ACCESS_TTL_SEC,
    }
    return jwt.encode(body, settings.JWT_ACCESS_SECRET, algorithm="HS256")


def sign_refresh(payload: JwtUserPayload) -> tuple[str, str]:
    now = _now()
    sid = str(uuid.uuid4())
    body = {
        "sub": payload.sub,
        "username": payload.username,
        "role": payload.role,
        "sid": sid,
        "type": "refresh",
        "iat": now,
        "exp": now + settings.REFRESH_TTL_SEC,
    }
    token = jwt.encode(body, settings.JWT_REFRESH_SECRET, algorithm="HS256")
    return token, sid


def verify_access(token: str) -> dict:
    try:
        data = jwt.decode(token, settings.JWT_ACCESS_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError as e:
        raise JwtError("Invalid token") from e
    if data.get("type") != "access":
        raise JwtError("Invalid token type")
    return data


def verify_refresh(token: str) -> dict:
    try:
        data = jwt.decode(token, settings.JWT_REFRESH_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError as e:
        raise JwtError("Invalid token") from e
    if data.get("type") != "refresh":
        raise JwtError("Invalid token type")
    if not data.get("sid"):
        raise JwtError("Missing sid")
    return data











