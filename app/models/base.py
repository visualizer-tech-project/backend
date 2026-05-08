from datetime import datetime, timezone
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict
from sqlalchemy import func, DateTime
from sqlmodel import Field, SQLModel

T = TypeVar('T', bound=SQLModel)


class BaseSQLModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={
            'server_default': func.now(),
            'nullable': False,
        },
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={
            'onupdate': func.now(),
            'server_default': func.now(),
            'nullable': False,
        },
    )


class BaseSchema(SQLModel):
    model_config = ConfigDict(from_attributes=True)


class BaseModelSchema(BaseSchema, BaseSQLModel):
    pass


class PaginationInfo(SQLModel):
    page: int
    pages_num: int
    total: int


class ListResponse(BaseModel, Generic[T]):
    info: PaginationInfo
    items: list[T]