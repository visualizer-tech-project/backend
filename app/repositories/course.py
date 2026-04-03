from typing import List, Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.course import Course, CourseCreate, CourseType, CourseUpdate
from app.repositories.base import BaseRepository, FilterCondition


class CourseRepository(BaseRepository[Course, CourseCreate, CourseUpdate]):
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
            skip: int = 0,
            limit: Optional[int] = None,
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
            skip: int = 0,
            limit: Optional[int] = None,
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