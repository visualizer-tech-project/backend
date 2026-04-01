from app.schemas.base import BaseSchema


class Token(BaseSchema):
    """Схема для JWT токена"""

    access_token: str
    token_type: str
    scope: str
