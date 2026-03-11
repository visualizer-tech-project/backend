from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel
from sqlalchemy.sql import func


class BaseModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column_kwargs={'server_default': func.now()}
    )