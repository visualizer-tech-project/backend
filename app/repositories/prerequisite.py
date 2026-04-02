from typing import List, Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.prerequisite import Prerequisite, PrerequisiteCreate, PrerequisitePublic
from app.repositories.base import BaseRepository


class PrerequisiteRepository(
    BaseRepository[Prerequisite, PrerequisiteCreate, PrerequisitePublic]
):
    def __init__(self, session: AsyncSession):
        super().__init__(Prerequisite, session)

    async def get_by_course_pair(
        self, course_id: int, prerequisite_course_id: int
    ) -> Optional[Prerequisite]:
        """Получить связь пререквизита по паре курсов."""
        items, _ = await self.get_all(
            filters={
                'course_id': course_id,
                'prerequisite_course_id': prerequisite_course_id,
            },
            limit=1,
        )
        return items[0] if items else None

    async def get_by_course(self, course_id: int) -> tuple[List[Prerequisite], int]:
        """Получить все пререквизиты курса."""
        return await self.get_all(filters={'course_id': course_id})

    async def get_by_prerequisite_course(
        self, prerequisite_course_id: int
    ) -> tuple[List[Prerequisite], int]:
        """Получить все связи, где курс является пререквизитом."""
        return await self.get_all(
            filters={'prerequisite_course_id': prerequisite_course_id}
        )

    async def get_prerequisite_ids(self, course_id: int) -> List[int]:
        """Получить список ID курсов-пререквизитов."""
        items, _ = await self.get_by_course(course_id)
        return [item.prerequisite_course_id for item in items]

    async def create_prerequisite(
        self, course_id: int, prerequisite_course_id: int
    ) -> Prerequisite:
        """Создать связь пререквизита."""
        prerequisite = Prerequisite(
            course_id=course_id,
            prerequisite_course_id=prerequisite_course_id,
        )
        return await self.save(prerequisite)

    async def delete_prerequisite(
        self, course_id: int, prerequisite_course_id: int
    ) -> bool:
        """Удалить связь пререквизита."""
        prerequisite = await self.get_by_course_pair(course_id, prerequisite_course_id)
        if not prerequisite:
            return False
        await self.session.delete(prerequisite)
        await self.session.commit()
        return True
