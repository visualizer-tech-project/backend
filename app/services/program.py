from app.core import exceptions
from app.models.base import ListResponse
from app.models.program import (
    Program,
    ProgramCreate,
    ProgramPublic,
    ProgramUpdate,
)
from app.models.course import Course
from app.schemas.filters import ProgramFilters
from app.schemas.program import ProgramCopyRequest
from app.repositories.program import ProgramRepository
from app.repositories.course import CourseRepository


class ProgramService:
    def __init__(
        self,
        program_repo: ProgramRepository,
        course_repo: CourseRepository,
    ) -> None:
        self._program_repo = program_repo
        self._course_repo = course_repo

    async def get_programs(
        self,
        filters: ProgramFilters,
    ) -> ListResponse[ProgramPublic]:
        result = await self._program_repo.get_filtered_paginated(filters)
        public_items = [ProgramPublic.model_validate(item) for item in result.items]
        return ListResponse[ProgramPublic](info=result.info, items=public_items)

    async def get_program_by_id(self, program_id: int) -> ProgramPublic:
        program = await self._program_repo.get_by_id(program_id)
        if not program:
            raise exceptions.NotFoundError('Program not found')
        return ProgramPublic.model_validate(program)

    async def create_program(
        self,
        program_data: ProgramCreate,
        user_id: int,
    ) -> ProgramPublic:
        existing = await self._program_repo.get_by_title(program_data.title)
        if existing:
            raise exceptions.ConflictError('Program with this title already exists')

        program = Program(
            title=program_data.title,
            description=program_data.description,
            user_id=user_id,
        )
        program = await self._program_repo.save(program)
        return ProgramPublic.model_validate(program)

    async def update_program(
        self,
        program_id: int,
        program_data: ProgramUpdate,
    ) -> ProgramPublic:
        program = await self._program_repo.get_by_id(program_id)
        if not program:
            raise exceptions.NotFoundError('Program not found')

        if program_data.title:
            existing = await self._program_repo.get_by_title(program_data.title)
            if existing and existing.id != program_id:
                raise exceptions.ConflictError('Program with this title already exists')

        update_dict = program_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(program, field, value)

        program = await self._program_repo.save(program)
        return ProgramPublic.model_validate(program)

    async def delete_program(self, program_id: int) -> None:
        deleted = await self._program_repo.delete(program_id)
        if not deleted:
            raise exceptions.NotFoundError('Program not found')

    async def copy_program(
            self,
            program_id: int,
            copy_request: ProgramCopyRequest,
            user_id: int,
    ) -> ProgramPublic:
        source_program = await self._program_repo.get_by_id(program_id)
        if not source_program:
            raise exceptions.NotFoundError('Source program not found')
        original_title = copy_request.title
        new_title = original_title
        counter = 1
        while await self._program_repo.get_by_title(new_title):
            new_title = f"{original_title} (копия {counter})"
            counter += 1
        new_program = Program(
            title=new_title,
            description=source_program.description,
            user_id=user_id,
        )
        new_program = await self._program_repo.save(new_program)
        courses, _ = await self._course_repo.get_by_program(program_id)
        for course in courses:
            new_course = Course(
                title=course.title,
                description=course.description,
                type=course.type,
                program_id=new_program.id,
                user_id=user_id,
            )
            await self._course_repo.save(new_course)
        new_program = await self._program_repo.get_by_id(new_program.id)
        return ProgramPublic.model_validate(new_program)
