# app/models/base.py
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func
from sqlmodel import Field, SQLModel


class BaseModel(SQLModel):
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
