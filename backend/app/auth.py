import logging
import os
import secrets

from fastapi import Depends, HTTPException, Request, Response, status
from itsdangerous import BadSignature, URLSafeSerializer
from passlib.hash import bcrypt

logger = logging.getLogger(__name__)

SESSION_COOKIE = "pm_session"
SALT = "pm-session"


def _secret_key() -> str:
    key = os.environ.get("SECRET_KEY")
    if key:
        return key
    logger.warning(
        "SECRET_KEY is not set; using insecure dev fallback. "
        "Set SECRET_KEY in production."
    )
    return "dev-only-secret"


def _signer() -> URLSafeSerializer:
    return URLSafeSerializer(_secret_key(), salt=SALT)


def _legacy_check(username: str, password: str) -> bool:
    return username == "user" and password == "password"


def validate_credentials(username: str, password: str) -> bool:
    from app.database import get_session_factory
    from sqlalchemy import select
    from app.models import User

    if _legacy_check(username, password):
        return True

    db = get_session_factory()()
    try:
        stmt = select(User).where(User.username == username)
        user = db.execute(stmt).scalar_one_or_none()
        if user is None:
            return False
        return bcrypt.verify(password, user.password_hash)
    finally:
        db.close()


def hash_password(password: str) -> str:
    return bcrypt.hash(password)


def create_session_cookie(response: Response, username: str) -> None:
    token = _signer().dumps({"username": username})
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        httponly=True,
        samesite="lax",
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(key=SESSION_COOKIE, path="/")


def read_session(request: Request) -> str | None:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    try:
        data = _signer().loads(token)
    except BadSignature:
        return None
    username = data.get("username") if isinstance(data, dict) else None
    return username if isinstance(username, str) else None


def get_current_user(request: Request) -> str:
    username = read_session(request)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return username


CurrentUser = Depends(get_current_user)
