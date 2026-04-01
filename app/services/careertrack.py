from typing import List, Optional

from app.models.user import User
from app.repositories.careertrack import CareerTrackRepository
from app.repositories.course import CourseRepository
from app.schemas.base import PageInfo, PaginatedResponse
from app.schemas.careertrack import (
    AddCourseToTrack,
    CareerTrackCreate,
    CareerTrackPublic,
    CareerTrackUpdate,
    CareerTrackWithCourses,
    TrackCourseItem,
)


class CareerTrackService:
    """Сервис управления карьерными треками"""

    def __init__(
        self, track_repo: CareerTrackRepository, course_repo: CourseRepository
    ):
        self.track_repo = track_repo
        self.course_repo = course_repo

    async def get_tracks(
        self,
        program_id: Optional[int] = None,
        title: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> PaginatedResponse[CareerTrackPublic]:
        """Получить список карьерных треков"""
        if title:
            tracks, total = await self.track_repo.search(title, skip, limit)
        else:
            tracks, total = await self.track_repo.get_all(
                skip=skip,
                limit=limit,
                order_by='created_at',
                descending=True,
            )

        return PaginatedResponse(
            items=tracks,
            page_info=PageInfo(total=total, offset=skip, limit=limit),
        )

    async def get_track_by_id(self, track_id: int) -> CareerTrackPublic:
        """Получить карьерный трек по ID"""
        track = await self.track_repo.get_by_id(track_id)
        if not track:
            raise ValueError('Career track not found')

        courses_count = await self.track_repo.get_courses_count(track_id)

        return CareerTrackPublic(
            id=track.id,
            title=track.title,
            description=track.description,
            user_id=track.user_id,
            courses_count=courses_count,
            created_at=track.created_at,
            updated_at=track.updated_at,
        )

    async def get_track_with_courses(
        self,
        track_id: int,
        skip_courses: int = 0,
        limit_courses: int = 100,
    ) -> CareerTrackWithCourses:
        """Получить карьерный трек со списком курсов"""
        track_with_courses = await self.track_repo.get_with_courses(
            track_id,
            skip_courses,
            limit_courses,
        )
        if not track_with_courses:
            raise ValueError('Career track not found')

        return track_with_courses

    async def create_track(
        self,
        track_data: CareerTrackCreate,
        current_user: User,
    ) -> CareerTrackPublic:
        """Создать новый карьерный трек"""
        if await self.track_repo.is_title_taken(track_data.title):
            raise ValueError('Track with this title already exists')

        track = await self.track_repo.create(track_data, current_user.id)

        return track

    async def update_track(
        self,
        track_id: int,
        track_data: CareerTrackUpdate,
        current_user: User,
    ) -> CareerTrackPublic:
        """Обновить карьерный трек"""
        track = await self.track_repo.get_by_id(track_id)
        if not track:
            raise ValueError('Career track not found')

        update_dict = track_data.model_dump(exclude_unset=True)
        if 'title' in update_dict:
            if await self.track_repo.is_title_taken(
                update_dict['title'],
                exclude_track_id=track_id,
            ):
                raise ValueError('Track with this title already exists')

        updated_track = await self.track_repo.update(track_id, track_data)
        if not updated_track:
            raise ValueError('Career track not found')

        courses_count = await self.track_repo.get_courses_count(track_id)

        return CareerTrackPublic(
            id=updated_track.id,
            title=updated_track.title,
            description=updated_track.description,
            user_id=updated_track.user_id,
            courses_count=courses_count,
            created_at=updated_track.created_at,
            updated_at=updated_track.updated_at,
        )

    async def delete_track(self, track_id: int) -> None:
        """Удалить карьерный трек"""
        deleted = await self.track_repo.delete(track_id)
        if not deleted:
            raise ValueError('Career track not found')

    async def get_track_courses(
        self,
        track_id: int,
    ) -> List[TrackCourseItem]:
        """Получить курсы в карьерном треке"""
        track = await self.track_repo.get_by_id(track_id)
        if not track:
            raise ValueError('Career track not found')

        return await self.track_repo.get_courses_with_order(track_id)

    async def add_course_to_track(
        self,
        track_id: int,
        add_data: AddCourseToTrack,
        current_user: User,
    ) -> dict:
        """Добавить курс в карьерный трек"""
        track = await self.track_repo.get_by_id(track_id)
        if not track:
            raise ValueError('Career track not found')

        course = await self.course_repo.get_by_id(add_data.course_id)
        if not course:
            raise ValueError('Course not found')

        track_course = await self.track_repo.add_course(
            track_id,
            add_data.course_id,
            add_data.order_index,
        )

        if not track_course:
            raise ValueError('Course already in track')

        return {
            'career_track_id': track_course.career_track_id,
            'course_id': track_course.course_id,
            'order_index': track_course.order_index,
            'created_at': track_course.created_at,
        }

    async def remove_course_from_track(
        self,
        track_id: int,
        course_id: int,
    ) -> None:
        """Удалить курс из карьерного трека"""
        removed = await self.track_repo.remove_course(track_id, course_id)
        if not removed:
            raise ValueError('Course not in track')
