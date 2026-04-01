from typing import List, Optional, Dict

from sqlalchemy.orm import selectinload
from sqlmodel import and_, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Course, UserProgressStatus
from app.models.careertrack import CareerTrack, CareerTrackCourse
from app.repositories.base import BaseRepository
from app.schemas.careertrack import CareerTrackCreate, CareerTrackUpdate


class CareerTrackRepository(
    BaseRepository[CareerTrack, CareerTrackCreate, CareerTrackUpdate]
):
    def __init__(self, session: AsyncSession):
        super().__init__(CareerTrack, session)

    async def get_by_title(self, title: str) -> Optional[CareerTrack]:
        """Получить карьерный трек по названию"""
        items, _ = await self.get_all(filters={'title': title}, limit=1)
        return items[0] if items else None

    async def get_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> tuple[List[CareerTrack], int]:
        """Получить треки, созданные пользователем"""
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
        """Получить связь трека с курсом"""
        query = select(CareerTrackCourse).where(
            and_(
                CareerTrackCourse.career_track_id == track_id,
                CareerTrackCourse.course_id == course_id,
            )
        )
        result = await self.session.exec(query)
        return result.first()

    async def get_track_courses(
        self,
        track_id: int,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> tuple[List[CareerTrackCourse], int]:
        """Получить все связи трека с курсами"""
        return await self._get_all_for_model(
            CareerTrackCourse,
            filters={'career_track_id': track_id},
            order_by='order_index',
            skip=skip,
            limit=limit,
        )

    async def create_track_course(
        self, track_id: int, course_id: int, order_index: int
    ) -> CareerTrackCourse:
        """Создать связь трека с курсом"""
        track_course = CareerTrackCourse(
            career_track_id=track_id,
            course_id=course_id,
            order_index=order_index,
        )
        self.session.add(track_course)
        await self.session.commit()
        await self.session.refresh(track_course)
        return track_course

    async def update_track_course_order(
        self, track_id: int, course_id: int, order_index: int
    ) -> Optional[CareerTrackCourse]:
        """Обновить порядок курса в треке"""
        track_course = await self.get_track_course(track_id, course_id)
        if not track_course:
            return None
        track_course.order_index = order_index
        self.session.add(track_course)
        await self.session.commit()
        await self.session.refresh(track_course)
        return track_course

    async def delete_track_course(self, track_id: int, course_id: int) -> bool:
        """Удалить связь трека с курсом"""
        track_course = await self.get_track_course(track_id, course_id)
        if not track_course:
            return False
        await self.session.delete(track_course)
        await self.session.commit()
        return True

    async def get_track_courses_count(self, track_id: int) -> int:
        """Получить количество курсов в треке"""
        query = (
            select(func.count())
            .select_from(CareerTrackCourse)
            .where(CareerTrackCourse.career_track_id == track_id)
        )
        return await self.session.scalar(query) or 0

    async def _get_all_for_model(
        self,
        model,
        skip: int = 0,
        limit: Optional[int] = None,
        filters: Optional[dict] = None,
        order_by: Optional[str] = None,
    ) -> tuple[List, int]:
        """Вспомогательный метод для получения записей из любой модели"""
        query = select(model)
        if filters:
            for field, value in filters.items():
                if hasattr(model, field) and value is not None:
                    query = query.where(getattr(model, field) == value)

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query) or 0

        if order_by and hasattr(model, order_by):
            query = query.order_by(getattr(model, order_by))

        if limit is not None:
            query = query.offset(skip).limit(limit)
        else:
            query = query.offset(skip)

        result = await self.session.exec(query)
        return result.all(), total

    async def get_track_with_courses(
            self,
            track_id: int,
            user_id: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Получить карьерный трек со всеми курсами и их прогрессом.

        Args:
            track_id: ID трека
            user_id: ID пользователя (опционально, для получения прогресса)

        Returns:
            Словарь с треком, курсами и прогрессом
        """

        query = (
            select(CareerTrack)
            .where(CareerTrack.id == track_id)
            .options(
                selectinload(CareerTrack.courses)
                .selectinload(CareerTrackCourse.course)
                .selectinload(Course.progress)
            )
        )

        result = await self.session.exec(query)
        track = result.first()

        if not track:
            return None

        track_courses = []
        for track_course in track.courses:
            course = track_course.course
            course_data = {
                'track_course_id': track_course.id,
                'order_index': track_course.order_index,
                'course': course,
                'prerequisites': [],
            }

            if user_id:
                user_progress = next(
                    (p for p in course.progress if p.user_id == user_id),
                    None
                )
                course_data['progress'] = user_progress
                course_data['is_completed'] = (
                        user_progress and user_progress.status == UserProgressStatus.COMPLETED
                )
                course_data['is_in_progress'] = (
                        user_progress and user_progress.status == UserProgressStatus.IN_PROGRESS
                )

            track_courses.append(course_data)

        track_courses.sort(key=lambda x: x['order_index'])

        return {
            'track': track,
            'courses': track_courses,
            'courses_count': len(track_courses),
        }