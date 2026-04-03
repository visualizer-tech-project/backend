from typing import List, Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.prerequisite import Prerequisite, PrerequisiteCreate
from app.repositories.base import BaseRepository, FilterCondition


class PrerequisiteRepository(
    BaseRepository[Prerequisite, PrerequisiteCreate, PrerequisiteCreate]
):
    def __init__(self, session: AsyncSession):
        super().__init__(Prerequisite, session)

    async def get_by_course_pair(
        self, course_id: int, prerequisite_course_id: int
    ) -> Optional[Prerequisite]:
        """Получить связь пререквизита по паре курсов."""
        filters = [
            FilterCondition('course_id', course_id),
            FilterCondition('prerequisite_course_id', prerequisite_course_id),
        ]
        items, _ = await self.get_all(filters=filters, limit=1)
        return items[0] if items else None

    async def get_by_course(self, course_id: int) -> List[Prerequisite]:
        """Получить все пререквизиты курса."""
        filters = [FilterCondition('course_id', course_id)]
        items, _ = await self.get_all(filters=filters)
        return items

    async def get_by_prerequisite_course(
        self, prerequisite_course_id: int
    ) -> List[Prerequisite]:
        """Получить все связи, где курс является пререквизитом."""
        filters = [FilterCondition('prerequisite_course_id', prerequisite_course_id)]
        items, _ = await self.get_all(filters=filters)
        return items

    async def get_prerequisite_ids(self, course_id: int) -> List[int]:
        """Получить список ID курсов-пререквизитов."""
        prerequisites = await self.get_by_course(course_id)
        return [item.prerequisite_course_id for item in prerequisites]

    async def add_prerequisite(
        self, course_id: int, prerequisite_course_id: int
    ) -> Prerequisite:
        """Создать связь пререквизита."""
        prerequisite = Prerequisite(
            course_id=course_id,
            prerequisite_course_id=prerequisite_course_id,
        )
        return await self.save(prerequisite)

    async def remove_prerequisite(
        self, course_id: int, prerequisite_course_id: int
    ) -> bool:
        """Удалить связь пререквизита."""
        prerequisite = await self.get_by_course_pair(course_id, prerequisite_course_id)
        if not prerequisite:
            return False
        await self.session.delete(prerequisite)
        await self.session.commit()
        return True