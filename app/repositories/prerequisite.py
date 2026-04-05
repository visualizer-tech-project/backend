from typing import List, Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.prerequisite import Prerequisite, PrerequisiteCreate
from app.repositories.base import BaseRepository, FilterCondition
from app.core.constants import DEFAULT_SKIP, DEFAULT_LIMIT


class PrerequisiteRepository(
    BaseRepository[Prerequisite, PrerequisiteCreate, PrerequisiteCreate]
):
    def __init__(self, session: AsyncSession):
        super().__init__(Prerequisite, session)

    async def get_by_course_pair(
        self, course_id: int, prerequisite_course_id: int
    ) -> Optional[Prerequisite]:
        filters = [
            FilterCondition('course_id', course_id),
            FilterCondition('prerequisite_course_id', prerequisite_course_id),
        ]
        items, _ = await self.get_all(filters=filters, limit=DEFAULT_LIMIT)
        return items[0] if items else None

    async def get_by_course(self, course_id: int) -> List[Prerequisite]:
        filters = [FilterCondition('course_id', course_id)]
        items, _ = await self.get_all(filters=filters)
        return items

    async def get_by_prerequisite_course(
        self, prerequisite_course_id: int
    ) -> List[Prerequisite]:
        filters = [FilterCondition('prerequisite_course_id', prerequisite_course_id)]
        items, _ = await self.get_all(filters=filters)
        return items

    async def get_prerequisite_ids(self, course_id: int) -> List[int]:
        prerequisites = await self.get_by_course(course_id)
        return [item.prerequisite_course_id for item in prerequisites]

    async def add_prerequisite(
        self, course_id: int, prerequisite_course_id: int
    ) -> Prerequisite:
        prerequisite = Prerequisite(
            course_id=course_id,
            prerequisite_course_id=prerequisite_course_id,
        )
        return await self.save(prerequisite)

    async def remove_prerequisite(
        self, course_id: int, prerequisite_course_id: int
    ) -> bool:
        prerequisite = await self.get_by_course_pair(course_id, prerequisite_course_id)
        if not prerequisite:
            return False
        await self.session.delete(prerequisite)
        await self.session.commit()
        return True
