"""
Authentication and JWT management module.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import get_settings

settings = get_settings()
security = HTTPBearer()


class JWTManager:
    """Manages JWT token creation and verification."""

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        """Initialize JWT manager."""
        self.secret_key = secret_key
        self.algorithm = algorithm

    def create_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Create JWT token."""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                seconds=settings.jwt_expiration
            )

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, self.secret_key, algorithm=self.algorithm
        )
        return encoded_jwt

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token."""
        try:
            payload = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )


# Global JWT manager instance
_jwt_manager: Optional[JWTManager] = None


def get_jwt_manager() -> JWTManager:
    """Get JWT manager instance."""
    global _jwt_manager
    if _jwt_manager is None:
        _jwt_manager = JWTManager(
            secret_key=settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )
    return _jwt_manager


def create_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create JWT token."""
    manager = get_jwt_manager()
    return manager.create_token(data, expires_delta)


def verify_token(token: str) -> Dict[str, Any]:
    """Verify JWT token."""
    manager = get_jwt_manager()
    return manager.verify_token(token)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """Dependency to get current user from token."""
    token = credentials.credentials
    try:
        payload = verify_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        return {"user_id": user_id, **payload}
    except HTTPException:
        raise


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[Dict[str, Any]]:
    """Dependency to optionally get user from token."""
    if credentials is None:
        return None

    token = credentials.credentials
    try:
        payload = verify_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return {"user_id": user_id, **payload}
    except HTTPException:
        return None
