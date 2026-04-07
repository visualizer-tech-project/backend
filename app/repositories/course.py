from typing import List, Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.course import Course, CourseCreate, CourseType, CourseUpdate
from app.repositories.base import BaseRepository, FilterCondition, ListResponse
from app.core.constants import DEFAULT_SKIP, DEFAULT_LIMIT
from app.schemas.filters import CourseFilters


class CourseRepository(BaseRepository[Course, CourseCreate, CourseCreate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Course, session)

    async def get_by_title(self, title: str) -> Optional[Course]:
        filters = [FilterCondition('title', title)]
        items, _ = await self.get_all(filters=filters, limit=DEFAULT_LIMIT)
        return items[0] if items else None

    async def get_by_program(
            self,
            program_id: int,
            skip: int = DEFAULT_SKIP,
            limit: int = DEFAULT_LIMIT,
            course_type: Optional[CourseType] = None,
    ) -> tuple[List[Course], int]:
        filters = [FilterCondition('program_id', program_id)]
        if course_type:
            filters.append(FilterCondition('type', course_type))

        return await self.get_all(
            skip=skip,
            limit=limit,
            filters=filters,
        )

    async def get_by_user(
            self,
            user_id: int,
            skip: int = DEFAULT_SKIP,
            limit: int = DEFAULT_LIMIT,
    ) -> tuple[List[Course], int]:
        filters = [FilterCondition('user_id', user_id)]
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by='created_at',
            descending=True,
        )

    async def get_filtered_paginated(
            self,
            filters: CourseFilters,
    ) -> ListResponse[Course]:
        filter_conditions = []

        if filters.program_id is not None:
            filter_conditions.append(FilterCondition('program_id', filters.program_id))
        if filters.type:
            filter_conditions.append(FilterCondition('type', filters.type))
        if filters.title:
            filter_conditions.append(FilterCondition('title', filters.title, 'contains'))

        return await self.get_paginated(
            skip=filters.skip,
            limit=filters.limit,
            filters=filter_conditions if filter_conditions else None,
            order_by='created_at',
            descending=True,
        )
