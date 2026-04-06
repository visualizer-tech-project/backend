from typing import List, Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.course import Course, CourseCreate, CourseType
from app.repositories.base import BaseRepository, FilterCondition
from app.repositories.base import DEFAULT_SKIP, DEFAULT_LIMIT


class CourseRepository(BaseRepository[Course, CourseCreate, CourseCreate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Course, session)

    async def get_by_title(self, title: str) -> Optional[Course]:
        """Получить курс по названию."""
        filters = [FilterCondition('title', title)]
        items, _ = await self.get_all(filters=filters, limit=1)
        return items[0] if items else None

    async def get_by_program(
            self,
            program_id: int,
            skip: int = DEFAULT_SKIP,
            limit: Optional[int] = DEFAULT_LIMIT,
            course_type: Optional[CourseType] = None,
    ) -> tuple[List[Course], int]:
        """Получить курсы по программе."""
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
            limit: Optional[int] = DEFAULT_LIMIT,
    ) -> tuple[List[Course], int]:
        """Получить курсы, созданные пользователем."""
        filters = [FilterCondition('user_id', user_id)]
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by='created_at',
            descending=True,
        )