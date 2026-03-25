from datetime import datetime
from typing import TypeVar

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Базовая схема со стандартной конфигурацией"""

    model_config = ConfigDict(from_attributes=True, extra='forbid')


class TimestampSchema(BaseSchema):
    """Схема с временными метками"""

    created_at: datetime


class BaseModelSchema(TimestampSchema):
    """Базовая схема для моделей с id"""

    id: int


class PageInfo(BaseSchema):
    """Информация о пагинации"""

    total: int
    offset: int
    limit: int


T = TypeVar('T')


class PaginatedResponse(BaseSchema):
    """Обертка для пагинированных ответов"""

    items: list[T]
    page_info: PageInfo
