from typing import Optional

from pydantic import Field

from app.schemas.base import BaseModelSchema, BaseSchema


class ProgramCreate(BaseSchema):
    """Схема для создания программы"""

    title: str = Field(
        ..., min_length=1, max_length=255, description='Название программы'
    )
    description: Optional[str] = Field(None, description='Описание программы')


class ProgramUpdate(BaseSchema):
    """Схема для обновления программы"""

    title: Optional[str] = Field(
        None, min_length=1, max_length=255, description='Название программы'
    )
    description: Optional[str] = Field(None, description='Описание программы')


class ProgramPublic(BaseModelSchema):
    """Публичная информация о программе"""

    title: str
    description: Optional[str] = None
    created_by: int


class ProgramCopyRequest(BaseSchema):
    """Схема для копирования программы"""

    title: str = Field(
        ..., min_length=1, max_length=255, description='Название новой программы'
    )
