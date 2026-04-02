from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_program_service
from app.models.user import User
from app.schemas.base import PaginatedResponse
from app.schemas.program import ProgramCreate, ProgramPublic, ProgramUpdate
from app.services.program import ProgramService

# Временная заглушка для текущего пользователя
DUMMY_USER = User(id=1, role='admin')

router = APIRouter(prefix='/programs', tags=['programs'])


@router.get(
    '/',
    response_model=PaginatedResponse[ProgramPublic],
    summary='Получить список образовательных программ',
)
async def get_programs(
    title: str = None,
    skip: int = 0,
    limit: int = 20,
    program_service: ProgramService = Depends(get_program_service),
) -> PaginatedResponse[ProgramPublic]:
    """Получить список программ с пагинацией и фильтрацией по названию."""
    return await program_service.get_programs(title, skip, limit)


@router.get(
    '/{program_id}',
    response_model=ProgramPublic,
    summary='Получить программу по ID',
)
async def get_program_by_id(
    program_id: int,
    program_service: ProgramService = Depends(get_program_service),
) -> ProgramPublic:
    """Получить информацию о программе по ID."""
    try:
        return await program_service.get_program_by_id(program_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    '/',
    response_model=ProgramPublic,
    status_code=status.HTTP_201_CREATED,
    summary='Создать новую программу',
)
async def create_program(
    program_data: ProgramCreate,
    program_service: ProgramService = Depends(get_program_service),
) -> ProgramPublic:
    """Создать новую образовательную программу."""
    try:
        return await program_service.create_program(program_data, DUMMY_USER)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put(
    '/{program_id}',
    response_model=ProgramPublic,
    summary='Обновить программу',
)
async def update_program(
    program_id: int,
    program_data: ProgramUpdate,
    program_service: ProgramService = Depends(get_program_service),
) -> ProgramPublic:
    """Обновить программу."""
    try:
        return await program_service.update_program(
            program_id, program_data, DUMMY_USER
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    '/{program_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Удалить программу',
)
async def delete_program(
    program_id: int,
    program_service: ProgramService = Depends(get_program_service),
) -> None:
    """Удалить программу."""
    try:
        await program_service.delete_program(program_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    '/{program_id}/copy',
    response_model=ProgramPublic,
    status_code=status.HTTP_201_CREATED,
    summary='Копировать программу для нового потока/года',
)
async def copy_program(
    program_id: int,
    copy_request: dict,
    program_service: ProgramService = Depends(get_program_service),
) -> ProgramPublic:
    """Скопировать программу со всеми курсами для нового потока."""
    try:
        new_title = copy_request.get('title')
        if not new_title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Title is required'
            )
        return await program_service.copy_program(program_id, new_title, DUMMY_USER)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
