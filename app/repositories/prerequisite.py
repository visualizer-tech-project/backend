from typing import List, Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.prerequisite import Prerequisite, PrerequisiteCreate, PrerequisiteUpdate
from app.repositories.base import BaseRepository
from app.core.constants import DEFAULT_LIMIT


class PrerequisiteRepository(
    BaseRepository[Prerequisite, PrerequisiteCreate, PrerequisiteUpdate]
):
    def __init__(self, session: AsyncSession):
        super().__init__(Prerequisite, session)

    def _setup_filters(self):
        self.add_filter('course_id')
        self.add_filter('prerequisite_course_id')

    async def get_by_course_pair(
        self, course_id: int, prerequisite_course_id: int
    ) -> Optional[Prerequisite]:
        filters = self._create_filter_conditions_from_dict(
            {
                'course_id': course_id,
                'prerequisite_course_id': prerequisite_course_id,
            }
        )
        items, _ = await self.get_all(filters=filters, limit=DEFAULT_LIMIT)
        return items[0] if items else None

    async def get_by_course(self, course_id: int) -> List[Prerequisite]:
        filters = self._create_filter_conditions_from_dict({'course_id': course_id})
        items, _ = await self.get_all(filters=filters)
        return items

    async def get_by_prerequisite_course(
        self, prerequisite_course_id: int
    ) -> List[Prerequisite]:
        filters = self._create_filter_conditions_from_dict(
            {'prerequisite_course_id': prerequisite_course_id}
        )
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
