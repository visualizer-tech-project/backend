import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import jwt
from fastapi import HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.settings import settings


class JWTHandler:

    @staticmethod
    def _get_current_time() -> datetime:
        return datetime.now(timezone.utc)

    @classmethod
    def create_access_token(cls, user_id: int, jti: Optional[str] = None) -> str:
        if jti is None:
            jti = str(uuid.uuid4())

        expire = cls._get_current_time() + timedelta(minutes=settings.access_token_expire_minutes)

        payload = {
            'sub': str(user_id),
            'jti': jti,
            'iat': int(cls._get_current_time().timestamp()),
            'exp': int(expire.timestamp()),
        }

        return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    @classmethod
    def create_refresh_token(cls, user_id: int, jti: Optional[str] = None) -> str:
        if jti is None:
            jti = str(uuid.uuid4())

        expire = cls._get_current_time() + timedelta(days=settings.refresh_token_expire_days)

        payload = {
            'sub': str(user_id),
            'jti': jti,
            'iat': int(cls._get_current_time().timestamp()),
            'exp': int(expire.timestamp()),
        }

        return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    @classmethod
    def decode_token(cls, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )
            return payload
        except jwt.PyJWTError:
            return None

    @classmethod
    def get_user_id_from_token(cls, token: str) -> Optional[int]:
        payload = cls.decode_token(token)
        if payload and 'sub' in payload:
            try:
                return int(payload['sub'])
            except (ValueError, TypeError):
                return None
        return None

    @classmethod
    def get_jti_from_token(cls, token: str) -> Optional[str]:
        payload = cls.decode_token(token)
        if payload:
            return payload.get('jti')
        return None

    @classmethod
    def is_token_expired(cls, token: str) -> bool:
        payload = cls.decode_token(token)
        if not payload:
            return True

        exp = payload.get('exp')
        if not exp:
            return True

        return cls._get_current_time().timestamp() > exp


class JWTBearer(HTTPBearer):

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        credentials: Optional[HTTPAuthorizationCredentials] = await super().__call__(request)

        if not credentials:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Not authenticated',
                    headers={'WWW-Authenticate': 'Bearer'},
                )
            return None

        if credentials.scheme.lower() != 'bearer':
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Invalid authentication scheme',
                    headers={'WWW-Authenticate': 'Bearer'},
                )
            return None

        token = credentials.credentials

        if JWTHandler.is_token_expired(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token has expired',
                headers={'WWW-Authenticate': 'Bearer'},
            )

        return token


jwt_bearer = JWTBearer()