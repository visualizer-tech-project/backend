from pydantic import Field

from app.models.base import BaseSchema


class ProgramCopyRequest(BaseSchema):
    """Схема для копирования программы"""

    title: str = Field(..., min_length=1, max_length=255)
