import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import jwt

from app.core.settings import settings


class JWTHandler:
    @staticmethod
    def _get_current_time() -> datetime:
        return datetime.now(timezone.utc)

    @classmethod
    def _create_token(
        cls,
        user_id: int,
        expire_delta: timedelta,
        jti: Optional[str] = None,
    ) -> str:
        if jti is None:
            jti = str(uuid.uuid4())

        expire = cls._get_current_time() + expire_delta

        payload = {
            'sub': str(user_id),
            'jti': jti,
            'iat': int(cls._get_current_time().timestamp()),
            'exp': int(expire.timestamp()),
        }

        return jwt.encode(
            payload,
            settings.auth.jwt_secret_key,
            algorithm=settings.auth.jwt_algorithm
        )

    @classmethod
    def create_access_token(cls, user_id: int, jti: Optional[str] = None) -> str:
        return cls._create_token(
            user_id,
            timedelta(minutes=settings.auth.access_token_expire_minutes),
            jti,
        )

    @classmethod
    def create_refresh_token(cls, user_id: int, jti: Optional[str] = None) -> str:
        return cls._create_token(
            user_id,
            timedelta(days=settings.auth.refresh_token_expire_days),
            jti,
        )

    @classmethod
    def decode_token(cls, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(
                token,
                settings.auth.jwt_secret_key,
                algorithms=[settings.auth.jwt_algorithm],
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