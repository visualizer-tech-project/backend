from typing import Optional
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    skip: int = Field(0, ge=0, description='Количество пропускаемых записей')
    limit: int = Field(20, ge=1, le=100, description='Лимит записей на странице')


class ProgramFilters(PaginationParams):
    title: Optional[str] = Field(None, description='Фильтр по названию')


class CourseFilters(PaginationParams):
    program_id: Optional[int] = Field(None, description='ID программы')
    type: Optional[str] = Field(None, description='Тип курса (required/elective)')
    title: Optional[str] = Field(None, description='Фильтр по названию')


class CareerTrackFilters(PaginationParams):
    title: Optional[str] = Field(None, description='Фильтр по названию')


class UserFilters(PaginationParams):
    role: Optional[str] = Field(None, description='Фильтр по роли')


class ProgressFilters(PaginationParams):
    status: Optional[str] = Field(None, description='Фильтр по статусу')
    program_id: Optional[int] = Field(None, description='Фильтр по программе')
