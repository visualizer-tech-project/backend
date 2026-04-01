from typing import Optional

from app.models.user import User
from app.repositories.program import ProgramRepository
from app.schemas.base import PageInfo, PaginatedResponse
from app.schemas.program import ProgramCreate, ProgramPublic, ProgramUpdate


class ProgramService:
    """Сервис управления образовательными программами"""

    def __init__(self, program_repo: ProgramRepository):
        self.program_repo = program_repo

    async def get_programs(
        self,
        title: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> PaginatedResponse[ProgramPublic]:
        """Получить список программ"""
        if title:
            programs, total = await self.program_repo.search(title, skip, limit)
        else:
            programs, total = await self.program_repo.get_all(
                skip=skip,
                limit=limit,
                order_by='created_at',
                descending=True,
            )

        return PaginatedResponse(
            items=[ProgramPublic.model_validate(program) for program in programs],
            page_info=PageInfo(total=total, offset=skip, limit=limit),
        )

    async def get_program_by_id(self, program_id: int) -> ProgramPublic:
        """Получить программу по ID"""
        program = await self.program_repo.get_by_id(program_id)
        if not program:
            raise ValueError('Program not found')

        return ProgramPublic.model_validate(program)

    async def create_program(
        self,
        program_data: ProgramCreate,
        current_user: User,
    ) -> ProgramPublic:
        """Создать новую программу"""
        if await self.program_repo.is_title_taken(program_data.title):
            raise ValueError('Program with this title already exists')

        program = await self.program_repo.create(program_data, current_user.id)

        return ProgramPublic.model_validate(program)

    async def update_program(
        self,
        program_id: int,
        program_data: ProgramUpdate,
        current_user: User,
    ) -> ProgramPublic:
        """Обновить программу"""
        program = await self.program_repo.get_by_id(program_id)
        if not program:
            raise ValueError('Program not found')

        update_dict = program_data.model_dump(exclude_unset=True)
        if 'title' in update_dict:
            if await self.program_repo.is_title_taken(
                update_dict['title'], exclude_program_id=program_id
            ):
                raise ValueError('Program with this title already exists')

        updated_program = await self.program_repo.update(program_id, program_data)
        if not updated_program:
            raise ValueError('Program not found')

        return ProgramPublic.model_validate(updated_program)

    async def delete_program(self, program_id: int) -> None:
        """Удалить программу"""
        deleted = await self.program_repo.delete(program_id)
        if not deleted:
            raise ValueError('Program not found')

    async def copy_program(
        self,
        program_id: int,
        new_title: str,
        current_user: User,
    ) -> ProgramPublic:
        """Скопировать программу для нового потока"""
        source_program = await self.program_repo.get_by_id(program_id)
        if not source_program:
            raise ValueError('Source program not found')

        if await self.program_repo.is_title_taken(new_title):
            raise ValueError('Program with this title already exists')

        new_program = await self.program_repo.copy_program(
            source_program_id=program_id,
            new_title=new_title,
            user_id=current_user.id,
        )

        if not new_program:
            raise ValueError('Failed to copy program')

        return ProgramPublic.model_validate(new_program)
