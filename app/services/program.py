from app.models.base import ListResponse
from app.models.program import (
    ProgramCreate,
    ProgramPublic,
    ProgramUpdate,
)
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
        result.items = [ProgramPublic.model_validate(item) for item in result.items]
        return result

    async def get_program_by_id(self, program_id: int) -> ProgramPublic:
        program = await self._program_repo.get_by_id(program_id)
        if not program:
            raise ValueError('Program not found')
        return ProgramPublic.model_validate(program)

    async def create_program(
            self,
            program_data: ProgramCreate,
            user_id: int,
    ) -> ProgramPublic:
        existing = await self._program_repo.get_by_title(program_data.title)
        if existing:
            raise ValueError('Program with this title already exists')

        program_dict = program_data.model_dump()
        program_dict['user_id'] = user_id

        program = await self._program_repo.create(program_dict)
        return ProgramPublic.model_validate(program)

    async def update_program(
        self,
        program_id: int,
        program_data: ProgramUpdate,
    ) -> ProgramPublic:
        program = await self._program_repo.get_by_id(program_id)
        if not program:
            raise ValueError('Program not found')

        if program_data.title:
            existing = await self._program_repo.get_by_title(program_data.title)
            if existing and existing.id != program_id:
                raise ValueError('Program with this title already exists')

        updated_program = await self._program_repo.update(program_id, program_data)
        if not updated_program:
            raise ValueError('Program not found')

        return ProgramPublic.model_validate(updated_program)

    async def delete_program(self, program_id: int) -> None:
        deleted = await self._program_repo.delete(program_id)
        if not deleted:
            raise ValueError('Program not found')

    async def copy_program(
        self,
        program_id: int,
        copy_request: ProgramCopyRequest,
        user_id: int,
    ) -> ProgramPublic:
        source_program = await self._program_repo.get_by_id(program_id)
        if not source_program:
            raise ValueError('Source program not found')

        existing = await self._program_repo.get_by_title(copy_request.title)
        if existing:
            raise ValueError('Program with this title already exists')

        program_dict = source_program.model_dump(exclude={'id', 'created_at', 'updated_at'})
        program_dict['title'] = copy_request.title
        program_dict['user_id'] = user_id

        new_program = await self._program_repo.create(program_dict)

        courses, _ = await self._course_repo.get_by_program(program_id)

        for course in courses:
            course_dict = course.model_dump(exclude={'id', 'created_at', 'updated_at'})
            course_dict['program_id'] = new_program.id
            course_dict['user_id'] = user_id
            await self._course_repo.create(course_dict)

        return ProgramPublic.model_validate(new_program)
