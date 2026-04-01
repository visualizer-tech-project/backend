from typing import List, Optional, Set, Dict

from sqlalchemy.orm import selectinload
from sqlmodel import and_, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import UserProgress, UserProgressStatus
from app.models.course import Course
from app.models.prerequisite import Prerequisite
from app.repositories.base import BaseRepository
from app.schemas.course import CourseCreate, CourseType, CourseUpdate


class CourseRepository(BaseRepository[Course, CourseCreate, CourseUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Course, session)

    async def get_by_title(self, title: str) -> Optional[Course]:
        """Получить курс по названию"""
        items, _ = await self.get_all(filters={'title': title}, limit=1)
        return items[0] if items else None

    async def get_by_program(
        self,
        program_id: int,
        skip: int = 0,
        limit: Optional[int] = None,
        course_type: Optional[CourseType] = None,
    ) -> tuple[List[Course], int]:
        """Получить курсы по программе"""
        filters = {'program_id': program_id}
        if course_type:
            filters['type'] = course_type
        return await self.get_all(skip=skip, limit=limit, filters=filters)

    async def get_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> tuple[List[Course], int]:
        """Получить курсы, созданные пользователем"""
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters={'user_id': user_id},
            order_by='created_at',
            descending=True,
        )

    async def get_prerequisite(
        self, course_id: int, prerequisite_course_id: int
    ) -> Optional[Prerequisite]:
        """Получить связь пререквизита"""
        query = select(Prerequisite).where(
            and_(
                Prerequisite.course_id == course_id,
                Prerequisite.prerequisite_course_id == prerequisite_course_id,
            )
        )
        result = await self.session.exec(query)
        return result.first()

    async def get_prerequisites_by_course(
        self, course_id: int
    ) -> tuple[List[Prerequisite], int]:
        """Получить все пререквизиты курса"""
        return await self._get_all_for_model(
            Prerequisite,
            filters={'course_id': course_id},
        )

    async def get_prerequisites_by_prerequisite_course(
        self, prerequisite_course_id: int
    ) -> tuple[List[Prerequisite], int]:
        """Получить все связи, где курс является пререквизитом"""
        return await self._get_all_for_model(
            Prerequisite,
            filters={'prerequisite_course_id': prerequisite_course_id},
        )

    async def create_prerequisite(
        self, course_id: int, prerequisite_course_id: int
    ) -> Prerequisite:
        """Создать связь пререквизита"""
        prerequisite = Prerequisite(
            course_id=course_id,
            prerequisite_course_id=prerequisite_course_id,
        )
        self.session.add(prerequisite)
        await self.session.commit()
        await self.session.refresh(prerequisite)
        return prerequisite

    async def delete_prerequisite(
        self, course_id: int, prerequisite_course_id: int
    ) -> bool:
        """Удалить связь пререквизита"""
        prerequisite = await self.get_prerequisite(course_id, prerequisite_course_id)
        if not prerequisite:
            return False
        await self.session.delete(prerequisite)
        await self.session.commit()
        return True

    async def get_prerequisites_ids(self, course_id: int) -> Set[int]:
        """Получить множество ID курсов-пререквизитов"""
        query = select(Prerequisite.prerequisite_course_id).where(
            Prerequisite.course_id == course_id
        )
        result = await self.session.exec(query)
        return set(result.all())

    async def get_courses_by_ids(self, ids: List[int]) -> List[Course]:
        """Получить курсы по списку ID"""
        if not ids:
            return []
        query = select(Course).where(Course.id.in_(ids))
        result = await self.session.exec(query)
        return result.all()

    async def is_title_taken_in_program(
        self,
        title: str,
        program_id: int,
        exclude_course_id: Optional[int] = None,
    ) -> bool:
        """Проверить, существует ли курс с таким названием в программе"""
        query = select(Course).where(
            and_(Course.title == title, Course.program_id == program_id)
        )
        if exclude_course_id:
            query = query.where(Course.id != exclude_course_id)
        result = await self.session.exec(query.limit(1))
        return result.first() is not None

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

    async def get_courses_with_prerequisites(
            self,
            course_ids: List[int]
    ) -> Dict[int, List[Course]]:
        """
        Получить словарь курсов с их пререквизитами.

        Args:
            course_ids: Список ID курсов

        Returns:
            Словарь {course_id: [prerequisite_courses]}
        """
        if not course_ids:
            return {}

        query = (
            select(Course)
            .where(Course.id.in_(course_ids))
            .options(
                selectinload(Course.prerequisites)
                .selectinload(Prerequisite.prerequisite_course)
            )
        )

        result = await self.session.exec(query)
        courses = result.all()

        courses_with_prereqs = {}
        for course in courses:
            prerequisites = [
                prereq.prerequisite_course
                for prereq in course.prerequisites
                if prereq.prerequisite_course
            ]
            courses_with_prereqs[course.id] = prerequisites

        return courses_with_prereqs

    async def get_available_courses(
            self,
            user_id: int,
            program_id: Optional[int] = None,
            skip: int = 0,
            limit: Optional[int] = None
    ) -> tuple[List[Course], int]:
        """
        Получить курсы, доступные для пользователя (с учетом пройденных пререквизитов).

        Args:
            user_id: ID пользователя
            program_id: ID программы (опционально)
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей

        Returns:
            Кортеж (список доступных курсов, общее количество)
        """

        completed_courses_subquery = (
            select(UserProgress.course_id)
            .where(
                and_(
                    UserProgress.user_id == user_id,
                    UserProgress.status == UserProgressStatus.COMPLETED
                )
            )
            .subquery()
        )

        prereq_query = select(Prerequisite)
        prereq_result = await self.session.exec(prereq_query)
        all_prereqs = prereq_result.all()

        prereqs_by_course: Dict[int, Set[int]] = {}
        for prereq in all_prereqs:
            if prereq.course_id not in prereqs_by_course:
                prereqs_by_course[prereq.course_id] = set()
            prereqs_by_course[prereq.course_id].add(prereq.prerequisite_course_id)

        completed_result = await self.session.exec(
            select(completed_courses_subquery.c.course_id).distinct()
        )
        completed_courses = set(completed_result.all())

        query = select(Course)

        if program_id:
            query = query.where(Course.program_id == program_id)

        result = await self.session.exec(query)
        all_courses = result.all()

        available_courses = []
        for course in all_courses:
            course_prereqs = prereqs_by_course.get(course.id, set())
            if not course_prereqs or course_prereqs.issubset(completed_courses):
                available_courses.append(course)

        total = len(available_courses)
        paginated_courses = available_courses[skip:skip + limit] if limit else available_courses[skip:]

        return paginated_courses, total

    async def get_courses_by_ids_with_progress(
            self,
            course_ids: List[int],
            user_id: int
    ) -> List[Dict]:
        """
        Получить курсы по списку ID с прогрессом пользователя.

        Args:
            course_ids: Список ID курсов
            user_id: ID пользователя

        Returns:
            Список словарей с курсами и их прогрессом
        """
        if not course_ids:
            return []

        query = (
            select(Course)
            .where(Course.id.in_(course_ids))
            .options(
                selectinload(Course.prerequisites)
                .selectinload(Prerequisite.prerequisite_course),
                selectinload(Course.progress)
            )
        )

        result = await self.session.exec(query)
        courses = result.all()

        courses_with_progress = []
        for course in courses:
            user_progress = next(
                (p for p in course.progress if p.user_id == user_id),
                None
            )

            prerequisites = [
                prereq.prerequisite_course
                for prereq in course.prerequisites
                if prereq.prerequisite_course
            ]

            courses_with_progress.append({
                'course': course,
                'progress': user_progress,
                'prerequisites': prerequisites,
                'is_completed': user_progress and user_progress.status == UserProgressStatus.COMPLETED,
                'is_in_progress': user_progress and user_progress.status == UserProgressStatus.IN_PROGRESS,
                'grade': user_progress.grade if user_progress else None,
            })

        return courses_with_progress