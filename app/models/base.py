from datetime import datetime, timezone
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict
from sqlalchemy import func
from sqlmodel import Field, SQLModel


class BaseSQLModel(SQLModel):
    """Базовая модель для БД"""

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={'server_default': func.now(), 'nullable': False},
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={
            'onupdate': func.now(),
            'server_default': func.now(),
            'nullable': False,
        },
    )


class BaseSchema(BaseModel):
    """Базовая схема со стандартной конфигурацией"""

    model_config = ConfigDict(from_attributes=True, extra='forbid')


class TimestampSchema(BaseSchema):
    """Схема с временными метками"""

    created_at: datetime
    updated_at: datetime


class BaseModelSchema(TimestampSchema):
    """Базовая схема для моделей с id"""

    id: int


class PaginationInfo(BaseSchema):
    """Информация о пагинации (page-based)"""

    total: int
    page: int
    pages_num: int


T = TypeVar('T')


class ListResponse(BaseSchema, Generic[T]):
    """Обертка для пагинированных ответов (как на фото)"""

    info: PaginationInfo
    items: list[T]


class PageInfo(BaseSchema):
    total: int
    offset: int
    limit: int


class PaginatedResponse(BaseSchema, Generic[T]):
    items: list[T]
    page_info: PageInfo
