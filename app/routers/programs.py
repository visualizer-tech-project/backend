from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_program_service
from app.models.base import PaginatedResponse
from app.models.filters import ProgramFilters
from app.models.program import ProgramCreate, ProgramPublic, ProgramUpdate, ProgramCopyRequest
from app.services.program import ProgramService

router = APIRouter(prefix='/programs', tags=['programs'])


@router.get('/', response_model=PaginatedResponse[ProgramPublic])
async def get_programs(
    filters: ProgramFilters = Depends(),
    service: ProgramService = Depends(get_program_service),
) -> PaginatedResponse[ProgramPublic]:
    return await service.get_programs(filters)


@router.get('/{program_id}', response_model=ProgramPublic)
async def get_program_by_id(
    program_id: int,
    service: ProgramService = Depends(get_program_service),
) -> ProgramPublic:
    try:
        return await service.get_program_by_id(program_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post('/', response_model=ProgramPublic, status_code=status.HTTP_201_CREATED)
async def create_program(
    program_data: ProgramCreate,
    service: ProgramService = Depends(get_program_service),
) -> ProgramPublic:
    try:
        return await service.create_program(program_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put('/{program_id}', response_model=ProgramPublic)
async def update_program(
    program_id: int,
    program_data: ProgramUpdate,
    service: ProgramService = Depends(get_program_service),
) -> ProgramPublic:
    try:
        return await service.update_program(program_id, program_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete('/{program_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_program(
    program_id: int,
    service: ProgramService = Depends(get_program_service),
) -> None:
    try:
        await service.delete_program(program_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post('/{program_id}/copy', response_model=ProgramPublic, status_code=status.HTTP_201_CREATED)
async def copy_program(
    program_id: int,
    copy_request: ProgramCopyRequest,
    service: ProgramService = Depends(get_program_service),
) -> ProgramPublic:
    try:
        return await service.copy_program(program_id, copy_request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))