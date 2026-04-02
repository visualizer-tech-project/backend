from typing import List, Optional

from app.models.user import User
from app.repositories.careertrack import CareerTrackRepository
from app.repositories.course import CourseRepository
from app.schemas.base import PageInfo, PaginatedResponse
from app.schemas.careertrack import (
    AddCourseToTrack,
    CareerTrackCoursePublic,
    CareerTrackCreate,
    CareerTrackPublic,
    CareerTrackUpdate,
    CareerTrackWithCourses,
    TrackCourseItem,
)
from app.schemas.course import CoursePublic


class CareerTrackService:
    """Сервис управления карьерными треками"""

    def __init__(
        self,
        track_repo: CareerTrackRepository,
        course_repo: CourseRepository,
    ):
        self.track_repo = track_repo
        self.course_repo = course_repo

    async def get_tracks(
        self,
        title: Optional[str] = None,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> PaginatedResponse[CareerTrackPublic]:
        """Получить список карьерных треков"""
        filters = {}
        if title:
            filters['title'] = title

        tracks, total = await self.track_repo.get_all(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by='created_at',
            descending=True,
        )

        result_items = []
        for track in tracks:
            courses_count = await self.track_repo.get_track_courses_count(track.id)
            result_items.append(
                CareerTrackPublic(
                    id=track.id,
                    title=track.title,
                    description=track.description,
                    user_id=track.user_id,
                    created_at=track.created_at,
                    updated_at=track.updated_at,
                    _courses_count=courses_count,
                )
            )

        return PaginatedResponse(
            items=result_items,
            page_info=PageInfo(total=total, offset=skip, limit=limit),
        )

    async def get_track_by_id(self, track_id: int) -> CareerTrackPublic:
        """Получить карьерный трек по ID"""
        track = await self.track_repo.get_by_id(track_id)
        if not track:
            raise ValueError('Career track not found')

        courses_count = await self.track_repo.get_track_courses_count(track_id)

        return CareerTrackPublic(
            id=track.id,
            title=track.title,
            description=track.description,
            user_id=track.user_id,
            created_at=track.created_at,
            updated_at=track.updated_at,
            _courses_count=courses_count,
        )

    async def get_track_with_courses(
        self,
        track_id: int,
        skip_courses: int = 0,
        limit_courses: Optional[int] = None,
    ) -> CareerTrackWithCourses:
        """Получить карьерный трек со списком курсов"""
        result = await self.track_repo.get_track_with_courses(track_id)
        if not result:
            raise ValueError('Career track not found')

        track = result['track']
        courses_data = result['courses']

        track_courses = []
        for idx, course_data in enumerate(courses_data):
            if idx < skip_courses:
                continue
            if (
                limit_courses is not None and len(track_courses) >= limit_courses
            ):  # ← проверка
                break

            course = course_data['course']
            track_courses.append(
                TrackCourseItem(
                    order_index=course_data['order_index'],
                    course=CoursePublic.model_validate(course),
                )
            )

        return CareerTrackWithCourses(
            id=track.id,
            title=track.title,
            description=track.description,
            user_id=track.user_id,
            created_at=track.created_at,
            updated_at=track.updated_at,
            _courses_count=len(courses_data),
            courses=track_courses,
        )

    async def create_track(
        self,
        track_data: CareerTrackCreate,
        current_user: User,
    ) -> CareerTrackPublic:
        """Создать новый карьерный трек"""
        existing, _ = await self.track_repo.get_all(
            filters={'title': track_data.title},
            limit=1,
        )
        if existing:
            raise ValueError('Track with this title already exists')

        track_dict = track_data.model_dump()
        track_dict['user_id'] = current_user.id

        track = await self.track_repo.create(track_dict)

        return CareerTrackPublic(
            id=track.id,
            title=track.title,
            description=track.description,
            user_id=track.user_id,
            created_at=track.created_at,
            updated_at=track.updated_at,
            _courses_count=0,
        )

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
            existing, _ = await self.track_repo.get_all(
                filters={'title': update_dict['title']},
                limit=1,
            )
            if existing and existing[0].id != track_id:
                raise ValueError('Track with this title already exists')

        updated_track = await self.track_repo.update(track_id, track_data)
        if not updated_track:
            raise ValueError('Career track not found')

        courses_count = await self.track_repo.get_track_courses_count(track_id)

        return CareerTrackPublic(
            id=updated_track.id,
            title=updated_track.title,
            description=updated_track.description,
            user_id=updated_track.user_id,
            created_at=updated_track.created_at,
            updated_at=updated_track.updated_at,
            _courses_count=courses_count,
        )

    async def delete_track(self, track_id: int) -> None:
        """Удалить карьерный трек"""
        deleted = await self.track_repo.delete(track_id)
        if not deleted:
            raise ValueError('Career track not found')

    async def get_track_courses(
        self,
        track_id: int,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> List[TrackCourseItem]:
        """Получить курсы в карьерном треке"""
        track = await self.track_repo.get_by_id(track_id)
        if not track:
            raise ValueError('Career track not found')

        track_courses, total = await self.track_repo.get_track_courses(
            track_id, skip, limit
        )

        result = []
        for tc in track_courses:
            result.append(
                TrackCourseItem(
                    order_index=tc.order_index,
                    course=CoursePublic.model_validate(tc.course),
                )
            )

        return result

    async def add_course_to_track(
        self,
        track_id: int,
        add_data: AddCourseToTrack,
        current_user: User,
    ) -> CareerTrackCoursePublic:
        """Добавить курс в карьерный трек"""
        track = await self.track_repo.get_by_id(track_id)
        if not track:
            raise ValueError('Career track not found')

        course = await self.course_repo.get_by_id(add_data.course_id)
        if not course:
            raise ValueError('Course not found')

        existing = await self.track_repo.get_track_course(track_id, add_data.course_id)
        if existing:
            raise ValueError('Course already in track')

        track_course = await self.track_repo.create_track_course(
            track_id, add_data.course_id, add_data.order_index
        )

        return CareerTrackCoursePublic(
            id=track_course.id,
            career_track_id=track_course.career_track_id,
            course_id=track_course.course_id,
            order_index=track_course.order_index,
            created_at=track_course.created_at,
            updated_at=track_course.updated_at,
        )

    async def remove_course_from_track(
        self,
        track_id: int,
        course_id: int,
    ) -> None:
        """Удалить курс из карьерного трека"""
        removed = await self.track_repo.delete_track_course(track_id, course_id)
        if not removed:
            raise ValueError('Course not in track')
