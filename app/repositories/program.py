from typing import Dict, List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import selectinload
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Prerequisite, UserProgressStatus
from app.models.course import Course
from app.models.program import Program
from app.repositories.base import BaseRepository
from app.schemas.program import ProgramCreate, ProgramUpdate


class ProgramRepository(BaseRepository[Program, ProgramCreate, ProgramUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Program, session)

    async def get_by_title(self, title: str) -> Optional[Program]:
        """Получить программу по названию"""
        items, _ = await self.get_all(filters={'title': title}, limit=1)
        return items[0] if items else None

    async def get_by_user(
        self, user_id: int, skip: int = 0, limit: Optional[int] = None
    ) -> tuple[List[Program], int]:
        """Получить программы, созданные пользователем"""
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters={'user_id': user_id},
            order_by='created_at',
            descending=True,
        )

    async def get_courses_by_program(
        self,
        program_id: int,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> tuple[List[Course], int]:
        """Получить курсы программы"""
        query = select(Course).where(Course.program_id == program_id)
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query) or 0

        if limit is not None:
            query = query.offset(skip).limit(limit)
        else:
            query = query.offset(skip)

        result = await self.session.exec(query)
        return result.all(), total

    async def get_courses_count(self, program_id: int) -> int:
        """Получить количество курсов в программе"""
        query = (
            select(func.count())
            .select_from(Course)
            .where(Course.program_id == program_id)
        )
        return await self.session.scalar(query) or 0

    async def is_title_taken(
        self, title: str, exclude_program_id: Optional[int] = None
    ) -> bool:
        """Проверить, занято ли название программы"""
        query = select(Program).where(Program.title == title)
        if exclude_program_id:
            query = query.where(Program.id != exclude_program_id)
        result = await self.session.exec(query.limit(1))
        return result.first() is not None

    async def get_program_with_courses(
        self,
        program_id: int,
        user_id: Optional[int] = None,
        include_courses: bool = True,
    ) -> Optional[Dict]:
        """
        Получить программу со всеми курсами и их прогрессом.

        Args:
            program_id: ID программы
            user_id: ID пользователя (опционально, для получения прогресса)
            include_courses: Включать ли курсы в результат

        Returns:
            Словарь с программой, курсами и статистикой
        """

        query = select(Program).where(Program.id == program_id)

        if include_courses:
            query = query.options(
                selectinload(Program.courses).selectinload(Course.progress)
            )

        result = await self.session.exec(query)
        program = result.first()

        if not program:
            return None

        response = {
            'program': program,
            'courses_count': 0,
            'courses': [],
        }

        if include_courses and program.courses:
            courses_data = []
            required_count = 0
            elective_count = 0
            completed_count = 0
            in_progress_count = 0

            for course in program.courses:
                if course.type.value == 'required':
                    required_count += 1
                else:
                    elective_count += 1
                course_data = {
                    'course': course,
                    'prerequisites': [],
                }
                if user_id:
                    user_progress = next(
                        (p for p in course.progress if p.user_id == user_id), None
                    )
                    course_data['progress'] = user_progress

                    if user_progress:
                        if user_progress.status == UserProgressStatus.COMPLETED:
                            completed_count += 1
                        elif user_progress.status == UserProgressStatus.IN_PROGRESS:
                            in_progress_count += 1

                courses_data.append(course_data)

            response.update(
                {
                    'courses': courses_data,
                    'courses_count': len(program.courses),
                    'required_courses_count': required_count,
                    'elective_courses_count': elective_count,
                    'completed_courses_count': completed_count,
                    'in_progress_courses_count': in_progress_count,
                    'completion_percentage': (
                        (completed_count / len(program.courses) * 100)
                        if program.courses
                        else 0
                    ),
                }
            )

        return response

    async def _get_prerequisite_by_courses(
        self, course_id: int, prerequisite_course_id: int
    ) -> Optional[Prerequisite]:
        """
        Вспомогательный метод для проверки существования пререквизита.
        """

        query = select(Prerequisite).where(
            and_(
                Prerequisite.course_id == course_id,
                Prerequisite.prerequisite_course_id == prerequisite_course_id,
            )
        )
        result = await self.session.exec(query)
        return result.first()
