from typing import Any, Dict, List, Optional, Set

from sqlmodel import and_, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.careertrack import CareerTrackCourse
from app.models.course import Course
from app.models.prerequisite import Prerequisite
from app.models.userprogress import UserProgress, UserProgressStatus
from app.repositories.base import BaseRepository
from app.schemas.course import CourseCreate, CourseType, CourseUpdate


class CourseRepository(BaseRepository[Course, CourseCreate, CourseUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Course, session)

    async def get_by_title(self, title: str) -> Optional[Course]:
        """Получить курс по названию"""
        query = select(Course).where(Course.title == title)
        result = await self.session.exec(query)
        return result.first()

    async def get_by_program(
        self,
        program_id: int,
        skip: int = 0,
        limit: int = 20,
        course_type: Optional[CourseType] = None,
    ) -> tuple[List[Course], int]:
        """Получить курсы по программе с возможной фильтрацией"""
        filters = {'program_id': program_id}
        if course_type:
            filters['type'] = course_type
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters=filters,
        )

    async def get_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Course], int]:
        """Получить курсы, созданные пользователем"""
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters={'user_id': user_id},
            order_by='created_at',
            descending=True,
        )

    async def search(
        self,
        query_str: str,
        program_id: Optional[int] = None,
        course_type: Optional[CourseType] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Course], int]:
        """Поиск курсов по названию и описанию с возможной фильтрацией"""
        search_pattern = f'%{query_str}%'

        base_query = select(Course).where(
            (Course.title.ilike(search_pattern))
            | (Course.description.ilike(search_pattern))
        )
        if program_id:
            base_query = base_query.where(Course.program_id == program_id)
        if course_type:
            base_query = base_query.where(Course.type == course_type)
        count_query = select(func.count()).select_from(base_query.subquery())
        total = await self.session.scalar(count_query) or 0
        query = base_query.offset(skip).limit(limit)
        result = await self.session.exec(query)
        items = result.all()
        return items, total

    async def get_with_prerequisites(
        self,
        course_id: int,
        include_prerequisite_for: bool = False,
    ) -> Optional[Course]:
        """
        Получить курс с его пререквизитами.
        Args:
            course_id: ID курса
            include_prerequisite_for: Включать ли курсы, для которых этот курс является пререквизитом
        """
        course = await self.get_by_id(course_id)
        if not course:
            return None
        await self.session.refresh(course, attribute_names=['prerequisites'])
        if include_prerequisite_for:
            await self.session.refresh(course, attribute_names=['prerequisite_for'])
        return course

    async def get_prerequisites_ids(self, course_id: int) -> Set[int]:
        """Получить множество ID курсов-пререквизитов для указанного курса"""
        query = select(Prerequisite.prerequisite_course_id).where(
            Prerequisite.course_id == course_id
        )
        result = await self.session.exec(query)
        return set(result.all())

    async def get_courses_with_prerequisites(
        self,
        course_ids: List[int],
    ) -> Dict[int, List[Course]]:
        """
        Получить словарь курсов с их пререквизитами для нескольких курсов.
        Returns:
            Словарь {course_id: [список курсов-пререквизитов]}
        """
        if not course_ids:
            return {}
        query = select(Prerequisite).where(Prerequisite.course_id.in_(course_ids))
        result = await self.session.exec(query)
        prerequisites = result.all()
        prereq_course_ids = {p.prerequisite_course_id for p in prerequisites}
        if prereq_course_ids:
            courses_query = select(Course).where(Course.id.in_(prereq_course_ids))
            courses_result = await self.session.exec(courses_query)
            courses_map = {c.id: c for c in courses_result.all()}
        else:
            courses_map = {}
        result_map = {course_id: [] for course_id in course_ids}
        for prereq in prerequisites:
            if prereq.prerequisite_course_id in courses_map:
                result_map[prereq.course_id].append(
                    courses_map[prereq.prerequisite_course_id]
                )
        return result_map

    async def get_available_for_user(
        self,
        user_id: int,
        program_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Course], int]:
        """
        Получить курсы, доступные для пользователя (учитывая выполненные пререквизиты).
        Args:
            user_id: ID пользователя
            program_id: ID программы
            skip, limit: Пагинация
        Returns:
            Кортеж (список доступных курсов, общее количество доступных курсов)
        """
        courses_query = select(Course).where(Course.program_id == program_id)
        courses_result = await self.session.exec(courses_query)
        all_courses = courses_result.all()
        if not all_courses:
            return [], 0
        completed_courses_query = select(UserProgress.course_id).where(
            and_(
                UserProgress.user_id == user_id,
                UserProgress.status == UserProgressStatus.COMPLETED,
            )
        )
        completed_result = await self.session.exec(completed_courses_query)
        completed_course_ids = set(completed_result.all())
        course_ids = [c.id for c in all_courses]
        prerequisites_map = await self.get_courses_with_prerequisites(course_ids)
        available_courses = []
        for course in all_courses:
            prereqs = prerequisites_map.get(course.id, [])
            prereq_ids = {p.id for p in prereqs}
            if prereq_ids.issubset(completed_course_ids):
                available_courses.append(course)
        total = len(available_courses)
        paginated_courses = available_courses[skip : skip + limit]
        return paginated_courses, total

    async def add_prerequisite(
        self,
        course_id: int,
        prerequisite_course_id: int,
    ) -> Optional[Prerequisite]:
        """
        Добавить пререквизит для курса.
        Args:
            course_id: ID курса
            prerequisite_course_id: ID курса-пререквизита
        Returns:
            Созданная связь пререквизита или None, если связь не может быть создана
        """
        course = await self.get_by_id(course_id)
        prerequisite_course = await self.get_by_id(prerequisite_course_id)
        if not course or not prerequisite_course:
            return None
        if await self._would_create_cycle(course_id, prerequisite_course_id):
            return None
        existing_query = select(Prerequisite).where(
            and_(
                Prerequisite.course_id == course_id,
                Prerequisite.prerequisite_course_id == prerequisite_course_id,
            )
        )
        existing = await self.session.exec(existing_query)
        if existing.first():
            return None
        prerequisite = Prerequisite(
            course_id=course_id,
            prerequisite_course_id=prerequisite_course_id,
        )
        self.session.add(prerequisite)
        await self.session.commit()
        await self.session.refresh(prerequisite)
        return prerequisite

    async def remove_prerequisite(
        self,
        course_id: int,
        prerequisite_course_id: int,
    ) -> bool:
        """Удалить пререквизит"""
        query = select(Prerequisite).where(
            and_(
                Prerequisite.course_id == course_id,
                Prerequisite.prerequisite_course_id == prerequisite_course_id,
            )
        )
        result = await self.session.exec(query)
        prerequisite = result.first()
        if not prerequisite:
            return False
        await self.session.delete(prerequisite)
        await self.session.commit()
        return True

    async def _would_create_cycle(
        self,
        course_id: int,
        prerequisite_course_id: int,
    ) -> bool:
        """Проверить, создаст ли добавление пререквизита циклическую зависимость"""
        if course_id == prerequisite_course_id:
            return True
        visited = set()
        stack = [prerequisite_course_id]
        while stack:
            current_id = stack.pop()
            if current_id in visited:
                continue
            visited.add(current_id)
            query = select(Prerequisite.prerequisite_course_id).where(
                Prerequisite.course_id == current_id
            )
            result = await self.session.exec(query)
            prereq_ids = result.all()
            for prereq_id in prereq_ids:
                if prereq_id == course_id:
                    return True
                if prereq_id not in visited:
                    stack.append(prereq_id)
        return False

    async def get_prerequisites_tree(self, course_id: int) -> Dict[str, Any]:
        """
        Получить дерево пререквизитов для курса.
        Returns:
            Словарь с информацией о курсе и его пререквизитах (рекурсивно)
        """
        course = await self.get_with_prerequisites(course_id)
        if not course:
            return {}

        def build_tree(c: Course, visited: Set[int]) -> Dict[str, Any]:
            if c.id in visited:
                return {'id': c.id, 'title': c.title, 'circular': True}
            visited.add(c.id)
            tree = {'id': c.id, 'title': c.title, 'prerequisites': []}
            for prereq in c.prerequisites:
                if prereq.prerequisite_course:
                    tree['prerequisites'].append(
                        build_tree(prereq.prerequisite_course, visited.copy())
                    )
            return tree

        return build_tree(course, set())

    async def get_by_career_track(
        self,
        track_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Course], int]:
        """Получить курсы, входящие в карьерный трек"""
        track_courses_query = (
            select(CareerTrackCourse.course_id)
            .where(CareerTrackCourse.career_track_id == track_id)
            .order_by(CareerTrackCourse.order_index)
        )
        result = await self.session.exec(track_courses_query)
        course_ids = result.all()
        total = len(course_ids)
        paginated_ids = course_ids[skip : skip + limit]
        if not paginated_ids:
            return [], total
        courses_query = select(Course).where(Course.id.in_(paginated_ids))
        courses_result = await self.session.exec(courses_query)
        courses = courses_result.all()
        id_to_course = {c.id: c for c in courses}
        ordered_courses = [
            id_to_course[cid] for cid in paginated_ids if cid in id_to_course
        ]
        return ordered_courses, total

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
