from typing import List, Optional, Tuple

from sqlmodel import and_, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.careertrack import CareerTrack, CareerTrackCourse
from app.models.course import Course
from app.models.userprogress import UserProgress, UserProgressStatus
from app.repositories.base import BaseRepository
from app.schemas.careertrack import (
    CareerTrackCreate,
    CareerTrackPublic,
    CareerTrackUpdate,
    CareerTrackWithCourses,
    PopularTrack,
    TrackCompletionCourse,
    TrackCompletionStatus,
    TrackCourseItem,
    TrackWithCoursesCount,
)
from app.schemas.course import CoursePublic


class CareerTrackRepository(
    BaseRepository[CareerTrack, CareerTrackCreate, CareerTrackUpdate]
):
    def __init__(self, session: AsyncSession):
        super().__init__(CareerTrack, session)

    async def get_by_title(self, title: str) -> Optional[CareerTrack]:
        """Получить карьерный трек по названию"""
        query = select(CareerTrack).where(CareerTrack.title == title)
        result = await self.session.exec(query)
        return result.first()

    async def get_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[CareerTrackPublic], int]:
        """Получить треки, созданные пользователем"""
        tracks, total = await self.get_all(
            skip=skip,
            limit=limit,
            filters={'user_id': user_id},
            order_by='created_at',
            descending=True,
        )

        result = []
        for track in tracks:
            courses_count = await self._get_courses_count(track.id)
            result.append(
                CareerTrackPublic(
                    id=track.id,
                    title=track.title,
                    description=track.description,
                    user_id=track.user_id,
                    courses_count=courses_count,
                    created_at=track.created_at,
                    updated_at=track.updated_at,
                )
            )

        return result, total

    async def search(
        self,
        query_str: str,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[CareerTrackPublic], int]:
        """Поиск треков по названию и описанию"""
        search_pattern = f'%{query_str}%'
        base_query = select(CareerTrack).where(
            (CareerTrack.title.ilike(search_pattern))
            | (CareerTrack.description.ilike(search_pattern))
        )

        count_query = select(func.count()).select_from(base_query.subquery())
        total = await self.session.scalar(count_query) or 0

        query = base_query.offset(skip).limit(limit).order_by(CareerTrack.title)
        result = await self.session.exec(query)
        tracks = result.all()

        result_list = []
        for track in tracks:
            courses_count = await self._get_courses_count(track.id)
            result_list.append(
                CareerTrackPublic(
                    id=track.id,
                    title=track.title,
                    description=track.description,
                    user_id=track.user_id,
                    courses_count=courses_count,
                    created_at=track.created_at,
                    updated_at=track.updated_at,
                )
            )

        return result_list, total

    async def get_with_courses(
        self,
        track_id: int,
        skip_courses: int = 0,
        limit_courses: int = 100,
    ) -> Optional[CareerTrackWithCourses]:
        """Получить трек со всеми его курсами"""
        track = await self.get_by_id(track_id)
        if not track:
            return None

        track_courses_query = (
            select(CareerTrackCourse)
            .where(CareerTrackCourse.career_track_id == track_id)
            .order_by(CareerTrackCourse.order_index)
        )
        track_courses_query = track_courses_query.offset(skip_courses).limit(
            limit_courses
        )
        result = await self.session.exec(track_courses_query)
        track_courses = result.all()

        courses_list = []
        if track_courses:
            course_ids = [tc.course_id for tc in track_courses]
            courses_query = select(Course).where(Course.id.in_(course_ids))
            courses_result = await self.session.exec(courses_query)
            courses = {c.id: c for c in courses_result.all()}

            for tc in track_courses:
                course = courses.get(tc.course_id)
                if course:
                    courses_list.append(
                        TrackCourseItem(
                            order_index=tc.order_index,
                            course=CoursePublic.model_validate(course),
                        )
                    )

        courses_count = await self._get_courses_count(track_id)

        return CareerTrackWithCourses(
            id=track.id,
            title=track.title,
            description=track.description,
            user_id=track.user_id,
            courses_count=courses_count,
            created_at=track.created_at,
            updated_at=track.updated_at,
            courses=courses_list,
        )

    async def add_course(
        self,
        track_id: int,
        course_id: int,
        order_index: int,
    ) -> Optional[CareerTrackCourse]:
        """Добавить курс в карьерный трек"""
        track = await self.get_by_id(track_id)
        course_query = select(Course).where(Course.id == course_id)
        course_result = await self.session.exec(course_query)
        course = course_result.first()

        if not track or not course:
            return None

        existing_query = select(CareerTrackCourse).where(
            and_(
                CareerTrackCourse.career_track_id == track_id,
                CareerTrackCourse.course_id == course_id,
            )
        )
        existing = await self.session.exec(existing_query)
        if existing.first():
            return None

        order_taken_query = select(CareerTrackCourse).where(
            and_(
                CareerTrackCourse.career_track_id == track_id,
                CareerTrackCourse.order_index == order_index,
            )
        )
        order_taken = await self.session.exec(order_taken_query)
        if order_taken.first():
            await self._shift_order_indices(track_id, order_index, 1)

        track_course = CareerTrackCourse(
            career_track_id=track_id,
            course_id=course_id,
            order_index=order_index,
        )
        self.session.add(track_course)
        await self.session.commit()
        await self.session.refresh(track_course)
        return track_course

    async def remove_course(
        self,
        track_id: int,
        course_id: int,
    ) -> bool:
        """Удалить курс из карьерного трека"""
        query = select(CareerTrackCourse).where(
            and_(
                CareerTrackCourse.career_track_id == track_id,
                CareerTrackCourse.course_id == course_id,
            )
        )
        result = await self.session.exec(query)
        track_course = result.first()

        if not track_course:
            return False

        order_index = track_course.order_index
        await self.session.delete(track_course)
        await self._shift_order_indices(track_id, order_index + 1, -1)
        await self.session.commit()
        return True

    async def update_course_order(
        self,
        track_id: int,
        course_id: int,
        new_order_index: int,
    ) -> Optional[CareerTrackCourse]:
        """Обновить порядковый номер курса в треке"""
        query = select(CareerTrackCourse).where(
            and_(
                CareerTrackCourse.career_track_id == track_id,
                CareerTrackCourse.course_id == course_id,
            )
        )
        result = await self.session.exec(query)
        track_course = result.first()

        if not track_course:
            return None

        old_order_index = track_course.order_index
        if old_order_index == new_order_index:
            return track_course

        if new_order_index < old_order_index:
            await self._shift_order_indices(
                track_id, new_order_index, 1, old_order_index - 1
            )
        else:
            await self._shift_order_indices(
                track_id, old_order_index + 1, -1, new_order_index
            )

        track_course.order_index = new_order_index
        self.session.add(track_course)
        await self.session.commit()
        await self.session.refresh(track_course)
        return track_course

    async def _shift_order_indices(
        self,
        track_id: int,
        start_index: int,
        delta: int,
        end_index: Optional[int] = None,
    ) -> None:
        """Сдвинуть order_index для курсов в треке"""
        query = select(CareerTrackCourse).where(
            and_(
                CareerTrackCourse.career_track_id == track_id,
                CareerTrackCourse.order_index >= start_index,
            )
        )
        if end_index is not None:
            query = query.where(CareerTrackCourse.order_index <= end_index)

        result = await self.session.exec(query)
        track_courses = result.all()

        for tc in track_courses:
            tc.order_index += delta
            self.session.add(tc)

    async def reorder_courses(
        self,
        track_id: int,
        course_ids: List[int],
    ) -> bool:
        """Полностью переупорядочить курсы в треке"""
        track = await self.get_by_id(track_id)
        if not track:
            return False

        query = select(CareerTrackCourse).where(
            CareerTrackCourse.career_track_id == track_id
        )
        result = await self.session.exec(query)
        existing_track_courses = {tc.course_id: tc for tc in result.all()}

        existing_course_ids = set(existing_track_courses.keys())
        provided_course_ids = set(course_ids)

        if existing_course_ids != provided_course_ids:
            return False

        for index, course_id in enumerate(course_ids):
            existing_track_courses[course_id].order_index = index
            self.session.add(existing_track_courses[course_id])

        await self.session.commit()
        return True

    async def get_courses_with_order(
        self,
        track_id: int,
    ) -> List[TrackCourseItem]:
        """Получить курсы в треке с их порядковыми номерами"""
        track_courses_query = (
            select(CareerTrackCourse)
            .where(CareerTrackCourse.career_track_id == track_id)
            .order_by(CareerTrackCourse.order_index)
        )

        result = await self.session.exec(track_courses_query)
        track_courses = result.all()

        if not track_courses:
            return []

        course_ids = [tc.course_id for tc in track_courses]
        courses_query = select(Course).where(Course.id.in_(course_ids))
        courses_result = await self.session.exec(courses_query)
        courses = {c.id: c for c in courses_result.all()}

        result_list = []
        for tc in track_courses:
            course = courses.get(tc.course_id)
            if course:
                result_list.append(
                    TrackCourseItem(
                        order_index=tc.order_index,
                        course=CoursePublic.model_validate(course),
                    )
                )

        return result_list

    async def get_track_completion_status(
        self,
        track_id: int,
        user_id: int,
    ) -> TrackCompletionStatus:
        """Получить статус прохождения трека пользователем"""
        courses_with_order = await self.get_courses_with_order(track_id)

        if not courses_with_order:
            return TrackCompletionStatus(
                total_courses=0,
                completed_courses=0,
                in_progress_courses=0,
                not_started_courses=0,
                completion_percentage=0,
                courses=[],
            )

        course_ids = [item.course.id for item in courses_with_order]

        progress_query = select(UserProgress).where(
            and_(
                UserProgress.user_id == user_id, UserProgress.course_id.in_(course_ids)
            )
        )
        progress_result = await self.session.exec(progress_query)
        progress_map = {p.course_id: p for p in progress_result.all()}

        completed = 0
        in_progress = 0
        not_started = 0
        courses_status = []

        for item in courses_with_order:
            course = item.course
            progress = progress_map.get(course.id)

            if not progress or progress.status == UserProgressStatus.NOT_STARTED:
                status = 'not_started'
                not_started += 1
            elif progress.status == UserProgressStatus.IN_PROGRESS:
                status = 'in_progress'
                in_progress += 1
            else:
                status = 'completed'
                completed += 1

            courses_status.append(
                TrackCompletionCourse(
                    order_index=item.order_index,
                    course_id=course.id,
                    course_title=course.title,
                    status=status,
                    grade=progress.grade if progress else None,
                    completed_at=progress.completed_at.isoformat()
                    if progress and progress.completed_at
                    else None,
                )
            )

        total = len(courses_with_order)
        completion_percentage = (completed / total * 100) if total > 0 else 0

        return TrackCompletionStatus(
            total_courses=total,
            completed_courses=completed,
            in_progress_courses=in_progress,
            not_started_courses=not_started,
            completion_percentage=round(completion_percentage, 2),
            courses=courses_status,
        )

    async def get_tracks_with_courses_count(
        self,
        skip: int = 0,
        limit: int = 20,
        user_id: Optional[int] = None,
    ) -> tuple[List[TrackWithCoursesCount], int]:
        """Получить треки с количеством курсов в каждом"""
        base_query = select(CareerTrack)
        if user_id:
            base_query = base_query.where(CareerTrack.user_id == user_id)

        count_query = select(func.count()).select_from(base_query.subquery())
        total = await self.session.scalar(count_query) or 0

        query = (
            base_query.offset(skip).limit(limit).order_by(CareerTrack.created_at.desc())
        )
        result = await self.session.exec(query)
        tracks = result.all()

        result_list = []
        for track in tracks:
            courses_count = await self._get_courses_count(track.id)
            result_list.append(
                TrackWithCoursesCount(
                    id=track.id,
                    title=track.title,
                    description=track.description,
                    user_id=track.user_id,
                    courses_count=courses_count,
                    created_at=track.created_at,
                )
            )

        return result_list, total

    async def get_popular_tracks(
        self,
        limit: int = 10,
    ) -> List[PopularTrack]:
        """Получить самые популярные треки (по количеству курсов)"""
        query = (
            select(
                CareerTrack,
                func.count(CareerTrackCourse.course_id).label('courses_count'),
            )
            .outerjoin(
                CareerTrackCourse, CareerTrack.id == CareerTrackCourse.career_track_id
            )
            .group_by(CareerTrack.id)
            .order_by(func.count(CareerTrackCourse.course_id).desc())
            .limit(limit)
        )

        result = await self.session.exec(query)
        items = result.all()

        popular_tracks = []
        for track, courses_count in items:
            popular_tracks.append(
                PopularTrack(
                    track=CareerTrackPublic(
                        id=track.id,
                        title=track.title,
                        description=track.description,
                        user_id=track.user_id,
                        courses_count=courses_count,
                        created_at=track.created_at,
                        updated_at=track.updated_at,
                    ),
                    courses_count=courses_count,
                )
            )

        return popular_tracks

    async def is_title_taken(
        self, title: str, exclude_track_id: Optional[int] = None
    ) -> bool:
        """Проверить, занято ли название трека"""
        query = select(CareerTrack).where(CareerTrack.title == title)
        if exclude_track_id:
            query = query.where(CareerTrack.id != exclude_track_id)
        result = await self.session.exec(query.limit(1))
        return result.first() is not None

    async def bulk_add_courses(
        self,
        track_id: int,
        course_ids_with_order: List[Tuple[int, int]],
    ) -> List[CareerTrackCourse]:
        """Массовое добавление курсов в трек"""
        track = await self.get_by_id(track_id)
        if not track:
            return []

        existing_query = select(CareerTrackCourse).where(
            CareerTrackCourse.career_track_id == track_id
        )
        existing_result = await self.session.exec(existing_query)
        existing_courses = {tc.course_id: tc for tc in existing_result.all()}

        existing_order_indices = {tc.order_index for tc in existing_result.all()}

        created = []

        try:
            for course_id, order_index in course_ids_with_order:
                if course_id in existing_courses:
                    continue

                if order_index in existing_order_indices:
                    await self._shift_order_indices(track_id, order_index, 1)
                    existing_order_indices = {
                        idx + 1 if idx >= order_index else idx
                        for idx in existing_order_indices
                    }

                track_course = CareerTrackCourse(
                    career_track_id=track_id,
                    course_id=course_id,
                    order_index=order_index,
                )
                self.session.add(track_course)
                created.append(track_course)
                existing_order_indices.add(order_index)

            await self.session.commit()

            for tc in created:
                await self.session.refresh(tc)

            return created

        except Exception:
            await self.session.rollback()
            return []

    async def _get_courses_count(self, track_id: int) -> int:
        """Получить количество курсов в треке"""
        count_query = (
            select(func.count())
            .select_from(CareerTrackCourse)
            .where(CareerTrackCourse.career_track_id == track_id)
        )
        return await self.session.scalar(count_query) or 0

    async def create(
        self, obj_in: CareerTrackCreate, user_id: int
    ) -> CareerTrackPublic:
        """Создать трек с указанием создателя"""
        track = CareerTrack(
            title=obj_in.title,
            description=obj_in.description,
            user_id=user_id,
        )
        self.session.add(track)
        await self.session.commit()
        await self.session.refresh(track)

        return CareerTrackPublic(
            id=track.id,
            title=track.title,
            description=track.description,
            user_id=track.user_id,
            courses_count=0,
            created_at=track.created_at,
            updated_at=track.updated_at,
        )
