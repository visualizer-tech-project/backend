from typing import List, Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.course import Course, CourseCreate, CourseType, CourseUpdate
from app.repositories.base import BaseRepository


class CourseRepository(BaseRepository[Course, CourseCreate, CourseUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Course, session)

    async def get_by_title(self, title: str) -> Optional[Course]:
        """Получить курс по названию."""
        items, _ = await self.get_all(filters={'title': title}, limit=1)
        return items[0] if items else None

    async def get_by_program(
        self,
        program_id: int,
        skip: int = 0,
        limit: Optional[int] = None,
        course_type: Optional[CourseType] = None,
    ) -> tuple[List[Course], int]:
        """Получить курсы по программе."""
        filters = {'program_id': program_id}
        if course_type:
            filters['type'] = course_type
        return await self.get_all(skip=skip, limit=limit, filters=filters)

    async def get_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> tuple[List[Course], int]:
        """Получить курсы, созданные пользователем."""
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters={'user_id': user_id},
            order_by='created_at',
            descending=True,
        )

    async def get_by_ids(self, ids: List[int]) -> List[Course]:
        """Получить курсы по списку ID."""
        if not ids:
            return []
        query = select(Course).where(Course.id.in_(ids))
        result = await self.session.exec(query)
        return result.all()
