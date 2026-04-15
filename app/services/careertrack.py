from app.models.base import ListResponse
from app.models.careertrack import (
    CareerTrackCreate,
    CareerTrackPublic,
    CareerTrackUpdate,
    CareerTrackCoursePublic,
    TrackCourseItem,
)
from app.schemas.careertrack import AddCourseToTrack
from app.schemas.filters import CareerTrackFilters
from app.repositories.careertrack import CareerTrackRepository
from app.repositories.course import CourseRepository
from app.core.constants import DEFAULT_SKIP, DEFAULT_LIMIT


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
    ) -> ListResponse[CareerTrackPublic]:
        result = await self._track_repo.get_filtered_paginated(filters)
        result.items = [CareerTrackPublic.model_validate(item) for item in result.items]
        return result

    async def get_track_by_id(self, track_id: int) -> CareerTrackPublic:
        track = await self._track_repo.get_by_id(track_id)
        if not track:
            raise ValueError('Career track not found')
        return CareerTrackPublic.model_validate(track)

    async def get_track_courses(
            self,
            track_id: int,
            skip: int = DEFAULT_SKIP,
            limit: int = DEFAULT_LIMIT,
    ) -> list[TrackCourseItem]:
        track = await self._track_repo.get_by_id(track_id)
        if not track:
            raise ValueError('Career track not found')

        track_courses, _ = await self._track_repo.get_track_courses(track_id, skip, limit)

        items = []
        for tc in track_courses:
            items.append(TrackCourseItem(career_track_course=tc))

        return items

    async def create_track(
            self,
            track_data: CareerTrackCreate,
            user_id: int,
    ) -> CareerTrackPublic:
        existing = await self._track_repo.get_by_title(track_data.title)
        if existing:
            raise ValueError('Track with this title already exists')

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

        track_course = await self._track_repo.add_course_to_track(
            track_id, add_data.course_id, add_data.order_index
        )

        return CareerTrackCoursePublic.model_validate(track_course)

    async def remove_course_from_track(self, track_id: int, course_id: int) -> None:
        removed = await self._track_repo.remove_course_from_track(track_id, course_id)
        if not removed:
            raise ValueError('Course not in track')
