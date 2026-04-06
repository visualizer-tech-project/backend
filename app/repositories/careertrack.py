from typing import List, Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.careertrack import (
    CareerTrack,
    CareerTrackCourse,
    CareerTrackCreate,
)
from app.repositories.base import BaseRepository, FilterCondition
from app.repositories.base import DEFAULT_SKIP, DEFAULT_LIMIT


class CareerTrackRepository(
    BaseRepository[CareerTrack, CareerTrackCreate, CareerTrackCreate]
):
    def __init__(self, session: AsyncSession):
        super().__init__(CareerTrack, session)

    async def get_by_title(self, title: str) -> Optional[CareerTrack]:
        """Получить карьерный трек по названию."""
        filters = [FilterCondition('title', title)]
        items, _ = await self.get_all(filters=filters, limit=1)
        return items[0] if items else None

    async def get_by_user(
            self,
            user_id: int,
            skip: int = DEFAULT_SKIP,
            limit: Optional[int] = DEFAULT_LIMIT,
    ) -> tuple[List[CareerTrack], int]:
        """Получить треки, созданные пользователем."""
        filters = [FilterCondition('user_id', user_id)]
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by='created_at',
            descending=True,
        )

    async def get_track_course(
            self, track_id: int, course_id: int
    ) -> Optional[CareerTrackCourse]:
        """Получить связь трека с курсом."""
        filters = [
            FilterCondition('career_track_id', track_id),
            FilterCondition('course_id', course_id),
        ]
        items, _ = await self.get_all_for_model(
            model=CareerTrackCourse,
            filters=filters,
            limit=1,
        )
        return items[0] if items else None

    async def get_track_courses(
            self,
            track_id: int,
            skip: int = DEFAULT_SKIP,
            limit: Optional[int] = DEFAULT_LIMIT,
    ) -> tuple[List[CareerTrackCourse], int]:
        """Получить все связи трека с курсами."""
        filters = [FilterCondition('career_track_id', track_id)]
        return await self.get_all_for_model(
            model=CareerTrackCourse,
            skip=skip,
            limit=limit,
            filters=filters,
            order_by='order_index',
            descending=False,
        )

    async def add_course_to_track(
            self, track_id: int, course_id: int, order_index: int
    ) -> CareerTrackCourse:
        """Создать связь трека с курсом."""
        track_course = CareerTrackCourse(
            career_track_id=track_id,
            course_id=course_id,
            order_index=order_index,
        )
        return await self.save(track_course)

    async def update_course_order(
            self, track_id: int, course_id: int, new_order_index: int
    ) -> Optional[CareerTrackCourse]:
        """Обновить порядок курса в треке."""
        track_course = await self.get_track_course(track_id, course_id)
        if not track_course:
            return None
        track_course.order_index = new_order_index
        return await self.save(track_course)

    async def remove_course_from_track(self, track_id: int, course_id: int) -> bool:
        """Удалить связь трека с курсом."""
        track_course = await self.get_track_course(track_id, course_id)
        if not track_course:
            return False
        await self.session.delete(track_course)
        await self.session.commit()
        return True