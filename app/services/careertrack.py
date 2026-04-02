from typing import List, Optional

from app.dependencies.current_user import get_current_user_id
from app.models.base import PageInfo, PaginatedResponse
from app.models.careertrack import (
    AddCourseToTrack,
    CareerTrackCoursePublic,
    CareerTrackCreate,
    CareerTrackPublic,
    CareerTrackUpdate,
    TrackCourseItem,
)
from app.models.course import CoursePublic
from app.models.filters import CareerTrackFilters
from app.repositories.careertrack import CareerTrackRepository
from app.repositories.course import CourseRepository


class CareerTrackService:
    def __init__(
        self,
        track_repo: CareerTrackRepository,
        course_repo: CourseRepository,
    ) -> None:
        self._track_repo = track_repo
        self._course_repo = course_repo

    async def get_tracks(
        self,
        filters: CareerTrackFilters,
    ) -> PaginatedResponse[CareerTrackPublic]:
        filter_dict = filters.model_dump(exclude={'skip', 'limit'}, exclude_none=True)

        tracks, total = await self._track_repo.get_all(
            skip=filters.skip,
            limit=filters.limit,
            filters=filter_dict if filter_dict else None,
            order_by='created_at',
            descending=True,
        )

        return PaginatedResponse(
            items=[CareerTrackPublic.model_validate(track) for track in tracks],
            page_info=PageInfo(total=total, offset=filters.skip, limit=filters.limit),
        )

    async def get_track_by_id(self, track_id: int) -> CareerTrackPublic:
        track = await self._track_repo.get_by_id(track_id)
        if not track:
            raise ValueError('Career track not found')
        return CareerTrackPublic.model_validate(track)

    async def get_track_courses(
        self,
        track_id: int,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> List[TrackCourseItem]:
        track = await self._track_repo.get_by_id(track_id)
        if not track:
            raise ValueError('Career track not found')

        track_courses, _ = await self._track_repo.get_track_courses(track_id, skip, limit)

        return [
            TrackCourseItem(
                order_index=tc.order_index,
                course=CoursePublic.model_validate(tc.course),
            )
            for tc in track_courses
        ]

    async def create_track(self, track_data: CareerTrackCreate) -> CareerTrackPublic:
        existing = await self._track_repo.get_by_title(track_data.title)
        if existing:
            raise ValueError('Track with this title already exists')

        user_id = await get_current_user_id()
        track_dict = track_data.model_dump()
        track_dict['user_id'] = user_id

        track = await self._track_repo.create(track_dict)
        return CareerTrackPublic.model_validate(track)

    async def update_track(
        self,
        track_id: int,
        track_data: CareerTrackUpdate,
    ) -> CareerTrackPublic:
        track = await self._track_repo.get_by_id(track_id)
        if not track:
            raise ValueError('Career track not found')

        if track_data.title:
            existing = await self._track_repo.get_by_title(track_data.title)
            if existing and existing.id != track_id:
                raise ValueError('Track with this title already exists')

        updated_track = await self._track_repo.update(track_id, track_data)
        if not updated_track:
            raise ValueError('Career track not found')

        return CareerTrackPublic.model_validate(updated_track)

    async def delete_track(self, track_id: int) -> None:
        deleted = await self._track_repo.delete(track_id)
        if not deleted:
            raise ValueError('Career track not found')

    async def add_course_to_track(
        self,
        track_id: int,
        add_data: AddCourseToTrack,
    ) -> CareerTrackCoursePublic:
        track = await self._track_repo.get_by_id(track_id)
        if not track:
            raise ValueError('Career track not found')

        course = await self._course_repo.get_by_id(add_data.course_id)
        if not course:
            raise ValueError('Course not found')

        existing = await self._track_repo.get_track_course(track_id, add_data.course_id)
        if existing:
            raise ValueError('Course already in track')

        track_course = await self._track_repo.create_track_course(
            track_id, add_data.course_id, add_data.order_index
        )

        return CareerTrackCoursePublic.model_validate(track_course)

    async def remove_course_from_track(self, track_id: int, course_id: int) -> None:
        removed = await self._track_repo.delete_track_course(track_id, course_id)
        if not removed:
            raise ValueError('Course not in track')