from typing import List, Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.careertrack import (
    CareerTrack,
    CareerTrackCourse,
    CareerTrackCreate,
    CareerTrackUpdate,
)
from app.repositories.base import BaseRepository


class CareerTrackRepository(
    BaseRepository[CareerTrack, CareerTrackCreate, CareerTrackUpdate]
):
    def __init__(self, session: AsyncSession):
        super().__init__(CareerTrack, session)

    async def get_by_title(self, title: str) -> Optional[CareerTrack]:
        """Получить карьерный трек по названию."""
        items, _ = await self.get_all(filters={'title': title}, limit=1)
        return items[0] if items else None

    async def get_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> tuple[List[CareerTrack], int]:
        """Получить треки, созданные пользователем."""
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters={'user_id': user_id},
            order_by='created_at',
            descending=True,
        )

    async def get_track_course(
        self, track_id: int, course_id: int
    ) -> Optional[CareerTrackCourse]:
        """Получить связь трека с курсом."""
        items, _ = await self._get_track_courses(
            track_id=track_id, course_id=course_id, limit=1
        )
        return items[0] if items else None

    async def get_track_courses(
        self,
        track_id: int,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> tuple[List[CareerTrackCourse], int]:
        """Получить все связи трека с курсами."""
        return await self._get_track_courses(track_id=track_id, skip=skip, limit=limit)

    async def _get_track_courses(
        self,
        track_id: Optional[int] = None,
        course_id: Optional[int] = None,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> tuple[List[CareerTrackCourse], int]:
        """Внутренний метод для получения связей трека с курсами."""
        filters = {}
        if track_id is not None:
            filters['career_track_id'] = track_id
        if course_id is not None:
            filters['course_id'] = course_id

        return await self._get_all_for_model(
            CareerTrackCourse,
            filters=filters,
            order_by='order_index',
            skip=skip,
            limit=limit,
        )

    async def create_track_course(
        self, track_id: int, course_id: int, order_index: int
    ) -> CareerTrackCourse:
        """Создать связь трека с курсом."""
        track_course = CareerTrackCourse(
            career_track_id=track_id,
            course_id=course_id,
            order_index=order_index,
        )
        return await self._save_track_course(track_course)

    async def update_track_course_order(
        self, track_id: int, course_id: int, order_index: int
    ) -> Optional[CareerTrackCourse]:
        """Обновить порядок курса в треке."""
        track_course = await self.get_track_course(track_id, course_id)
        if not track_course:
            return None
        track_course.order_index = order_index
        return await self._save_track_course(track_course)

    async def _save_track_course(
        self, track_course: CareerTrackCourse
    ) -> CareerTrackCourse:
        """Сохранить связь трека с курсом."""
        self.session.add(track_course)
        await self.session.commit()
        await self.session.refresh(track_course)
        return track_course

    async def delete_track_course(self, track_id: int, course_id: int) -> bool:
        """Удалить связь трека с курсом."""
        track_course = await self.get_track_course(track_id, course_id)
        if not track_course:
            return False
        await self.session.delete(track_course)
        await self.session.commit()
        return True

    async def get_track_courses_count(self, track_id: int) -> int:
        """Получить количество курсов в треке."""
        _, total = await self.get_track_courses(track_id)
        return total
