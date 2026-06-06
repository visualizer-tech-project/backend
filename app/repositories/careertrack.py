from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.careertrack import (
    CareerTrack,
    CareerTrackCourse,
    CareerTrackCreate,
)
from app.models.user import User
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

    async def get_by_id(self, item_id: int) -> Optional[CareerTrack]:
        query = (
            select(CareerTrack)
            .join(User, CareerTrack.user_id == User.id)
            .where(CareerTrack.id == item_id)
            .options(selectinload(CareerTrack.user))
        )
        result = await self.session.exec(query)
        return result.first()

    async def get_all(
        self,
        skip: int = DEFAULT_SKIP,
        limit: int = DEFAULT_LIMIT,
        filters=None,
        order_by: Optional[str] = None,
        descending: bool = False,
    ) -> tuple[List[CareerTrack], int]:
        query = select(CareerTrack).join(User, CareerTrack.user_id == User.id).options(
            selectinload(CareerTrack.user)
        )
        query = self._apply_filters(query, CareerTrack, filters)

        count_query = select(func.count()).select_from(CareerTrack).join(
            User, CareerTrack.user_id == User.id
        )
        count_query = self._apply_filters(count_query, CareerTrack, filters)
        total = await self.session.scalar(count_query) or 0

        if order_by and hasattr(CareerTrack, order_by):
            order_field = getattr(CareerTrack, order_by)
            query = query.order_by(order_field.desc() if descending else order_field)

        if limit > 0:
            query = query.limit(limit)
        query = query.offset(skip)

        result = await self.session.exec(query)
        return result.all(), total

    async def get_by_title(self, title: str) -> Optional[CareerTrack]:
        query = (
            select(CareerTrack)
            .where(CareerTrack.title == title)
            .limit(1)
        )
        result = await self.session.exec(query)
        return result.first()

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
