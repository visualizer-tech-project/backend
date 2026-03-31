from typing import List, Optional

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.course import Course
from app.models.program import Program
from app.repositories.base import BaseRepository
from app.schemas.program import ProgramCreate, ProgramUpdate


class ProgramRepository(BaseRepository[Program, ProgramCreate, ProgramUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Program, session)

    async def get_by_title(self, title: str) -> Optional[Program]:
        """Получить программу по названию"""
        query = select(Program).where(Program.title == title)
        result = await self.session.exec(query)
        return result.first()

    async def get_by_user(
        self, user_id: int, skip: int = 0, limit: int = 20
    ) -> tuple[List[Program], int]:
        """Получить программы, созданные пользователем"""
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
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Program], int]:
        """Поиск программ по названию и описанию с фильтрацией по году набора"""
        search_pattern = f'%{query_str}%'
        base_query = select(Program).where(
            (Program.title.ilike(search_pattern))
            | (Program.description.ilike(search_pattern))
        )
        count_query = select(func.count()).select_from(base_query.subquery())
        total = await self.session.scalar(count_query) or 0
        query = base_query.offset(skip).limit(limit).order_by(Program.title)
        result = await self.session.exec(query)
        items = result.all()
        return items, total

    async def get_with_courses(
        self,
        program_id: int,
        skip_courses: int = 0,
        limit_courses: int = 100,
    ) -> Optional[Program]:
        """Получить программу со всеми её курсами"""
        program = await self.get_by_id(program_id)
        if not program:
            return None
        query = select(Course).where(Course.program_id == program_id)
        query = query.offset(skip_courses).limit(limit_courses).order_by(Course.title)
        result = await self.session.exec(query)
        courses = result.all()
        program.courses = courses
        return program

    async def get_courses_count(self, program_id: int) -> int:
        """Получить количество курсов в программе"""
        query = (
            select(func.count())
            .select_from(Course)
            .where(Course.program_id == program_id)
        )
        return await self.session.scalar(query) or 0

    async def get_programs_with_courses_count(
        self, skip: int = 0, limit: int = 20
    ) -> tuple[List[tuple[Program, int]], int]:
        """
        Получить программы с количеством курсов в каждой.
        Returns:
            Кортеж (список кортежей (программа, количество_курсов),
                общее_количество_программ)
        """
        base_query = select(Program)
        count_query = select(func.count()).select_from(base_query.subquery())
        total = await self.session.scalar(count_query) or 0
        query = base_query.offset(skip).limit(limit).order_by(Program.created_at.desc())
        result = await self.session.exec(query)
        programs = result.all()
        result_list = []
        for program in programs:
            courses_count = await self.get_courses_count(program.id)
            result_list.append((program, courses_count))
        return result_list, total

    async def copy_program(
        self,
        source_program_id: int,
        new_title: str,
        user_id: int,
    ) -> Optional[Program]:
        """
        Копировать программу со всеми курсами.

        Args:
            source_program_id: ID исходной программы
            new_title: Название новой программы
            new_admission_year: Год набора новой программы
            user_id: ID пользователя, создающего копию

        Returns:
            Новая программа или None, если исходная не найдена
        """
        source_program = await self.get_with_courses(source_program_id)
        if not source_program:
            return None
        new_program = Program(
            title=new_title,
            description=source_program.description,
            user_id=user_id,
        )
        self.session.add(new_program)
        await self.session.flush()
        for source_course in source_program.courses:
            new_course = Course(
                title=source_course.title,
                description=source_course.description,
                type=source_course.type,
                program_id=new_program.id,
                user_id=user_id,
            )
            self.session.add(new_course)
        await self.session.commit()
        await self.session.refresh(new_program)
        return new_program

    async def get_by_ids_with_courses(
        self,
        program_ids: List[int],
        skip_courses: int = 0,
        limit_courses: int = 100,
    ) -> List[Program]:
        """Получить несколько программ с их курсами"""
        if not program_ids:
            return []
        query = select(Program).where(Program.id.in_(program_ids))
        result = await self.session.exec(query)
        programs = result.all()
        for program in programs:
            courses_query = select(Course).where(Course.program_id == program.id)
            courses_query = (
                courses_query.offset(skip_courses)
                .limit(limit_courses)
            )
            courses_result = await self.session.exec(courses_query)
            program.courses = courses_result.all()
        return programs

    async def is_title_taken(
        self, title: str, exclude_program_id: Optional[int] = None
    ) -> bool:
        """
        Проверить, занято ли название программы.

        Args:
            title: Название для проверки
            exclude_program_id: ID программы, которую нужно исключить из проверки
        """
        query = select(Program).where(Program.title == title)
        if exclude_program_id:
            query = query.where(Program.id != exclude_program_id)
        result = await self.session.exec(query.limit(1))
        return result.first() is not None
