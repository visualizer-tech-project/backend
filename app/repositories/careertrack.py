from typing import List, Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.careertrack import (
    CareerTrack,
    CareerTrackCourse,
    CareerTrackCreate,
)
from app.repositories.base import BaseRepository, ListResponse
from app.core.constants import DEFAULT_SKIP, DEFAULT_LIMIT, FILTER_OPERATOR_CONTAINS
from app.schemas.filters import CareerTrackFilters


class CareerTrackRepository(
    BaseRepository[CareerTrack, CareerTrackCreate, CareerTrackCreate]
):
    def __init__(self, session: AsyncSession):
        super().__init__(CareerTrack, session)

    def _setup_filters(self):
        self.add_filter('title', operator=FILTER_OPERATOR_CONTAINS)
        self.add_filter('user_id')

    async def get_by_title(self, title: str) -> Optional[CareerTrack]:
        filters = self._create_filter_conditions_from_dict({'title': title})
        items, _ = await self.get_all(filters=filters, limit=DEFAULT_LIMIT)
        return items[0] if items else None

    async def get_by_user(
        self,
        user_id: int,
        skip: int = DEFAULT_SKIP,
        limit: int = DEFAULT_LIMIT,
    ) -> tuple[List[CareerTrack], int]:
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
        filters: CareerTrackFilters,
    ) -> ListResponse[CareerTrack]:
        filter_conditions = self._create_filter_conditions_from_model(filters)

        return await self.get_paginated(
            skip=filters.skip,
            limit=filters.limit,
            filters=filter_conditions if filter_conditions else None,
            order_by='created_at',
            descending=True,
        )

    async def get_track_course(
        self, track_id: int, course_id: int
    ) -> Optional[CareerTrackCourse]:
        filters = self._create_filter_conditions_from_dict(
            {
                'career_track_id': track_id,
                'course_id': course_id,
            }
        )
        items, _ = await self.get_all_for_model(
            model=CareerTrackCourse,
            filters=filters,
            limit=DEFAULT_LIMIT,
        )
        return items[0] if items else None

    async def get_track_courses(
        self,
        track_id: int,
        skip: int = DEFAULT_SKIP,
        limit: int = DEFAULT_LIMIT,
    ) -> tuple[List[CareerTrackCourse], int]:
        filters = self._create_filter_conditions_from_dict(
            {'career_track_id': track_id}
        )
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
        track_course = CareerTrackCourse(
            career_track_id=track_id,
            course_id=course_id,
            order_index=order_index,
        )
        return await self.save(track_course)

    async def update_course_order(
        self, track_id: int, course_id: int, new_order_index: int
    ) -> Optional[CareerTrackCourse]:
        track_course = await self.get_track_course(track_id, course_id)
        if not track_course:
            return None
        track_course.order_index = new_order_index
        return await self.save(track_course)

    async def remove_course_from_track(self, track_id: int, course_id: int) -> bool:
        track_course = await self.get_track_course(track_id, course_id)
        if not track_course:
            return False
        await self.session.delete(track_course)
        await self.session.commit()
        return True
