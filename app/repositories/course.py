from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.course import Course, CourseCreate, CourseType
from app.repositories.base import BaseRepository, ListResponse, FilterCondition
from app.core.constants import DEFAULT_SKIP, DEFAULT_LIMIT, FILTER_OPERATOR_CONTAINS
from app.schemas.filters import CourseFilters


class CourseRepository(BaseRepository[Course, CourseCreate, CourseCreate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Course, session)

    def _setup_filters(self):
        self.add_filter('title', operator=FILTER_OPERATOR_CONTAINS)
        self.add_filter('program_id')
        self.add_filter('type')
        self.add_filter('user_id')

    async def get_by_title(self, title: str) -> Optional[Course]:
        filters = self._create_filter_conditions_from_dict({'title': title})
        items, _ = await self.get_all(filters=filters, limit=DEFAULT_LIMIT)
        return items[0] if items else None

    async def get_by_title_and_program(self, title: str, program_id: int) -> Optional[Course]:
        filters = self._create_filter_conditions_from_dict({
            'title': title,
            'program_id': program_id
        })
        items, _ = await self.get_all(filters=filters, limit=1)
        return items[0] if items else None

    async def get_by_program(
        self,
        program_id: int,
        skip: int = DEFAULT_SKIP,
        limit: int = DEFAULT_LIMIT,
        course_type: Optional[CourseType] = None,
    ) -> tuple[List[Course], int]:
        filter_dict = {'program_id': program_id}
        if course_type:
            filter_dict['type'] = course_type

        filters = self._create_filter_conditions_from_dict(filter_dict)
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
        filters = self._create_filter_conditions_from_dict({'user_id': user_id})
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
        filter_conditions = self._create_filter_conditions_from_model(filters)

        return await self.get_paginated(
            skip=filters.skip,
            limit=filters.limit,
            filters=filter_conditions if filter_conditions else None,
            order_by='created_at',
            descending=True,
        )

    async def get_all(
            self,
            skip: int = DEFAULT_SKIP,
            limit: int = DEFAULT_LIMIT,
            filters: Optional[List[FilterCondition]] = None,
            order_by: Optional[str] = None,
            descending: bool = False,
    ) -> tuple[List[Course], int]:
        query = select(self.model).options(selectinload(Course.program), selectinload(Course.user))
        query = self._apply_filters(query, self.model, filters)
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query) or 0
        if order_by and hasattr(self.model, order_by):
            order_field = getattr(self.model, order_by)
            if descending:
                query = query.order_by(order_field.desc())
            else:
                query = query.order_by(order_field)
        if limit > 0:
            query = query.limit(limit)
        query = query.offset(skip)
        result = await self.session.exec(query)
        items = result.all()
        return items, total