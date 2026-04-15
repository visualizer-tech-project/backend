from typing import Annotated

from fastapi import APIRouter, Depends, Security, status

from app.core import responses
from app.core.security import get_current_user, CurrentUser
from app.dependencies import get_program_service
from app.models.base import ListResponse
from app.models.program import ProgramCreate, ProgramPublic, ProgramUpdate
from app.schemas.filters import ProgramFilters
from app.schemas.program import ProgramCopyRequest
from app.services.program import ProgramService

router = APIRouter(prefix='/programs', tags=['programs'])


@router.get(
    '/',
    response_model=ListResponse[ProgramPublic],
    responses={
        **responses.auth_responses,
        **responses.common_responses,
    }
)
async def get_programs(
    filters: ProgramFilters = Depends(),
    service: ProgramService = Depends(get_program_service),
    current_user: Annotated[
        CurrentUser,
        Security(get_current_user, scopes=['programs:list'])
    ] = None,
) -> ListResponse[ProgramPublic]:
    if current_user is None:
        responses.raise_forbidden()
    return await service.get_programs(filters)


@router.get(
    '/{program_id}',
    response_model=ProgramPublic,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.common_responses,
    }
)
async def get_program_by_id(
    program_id: int,
    service: ProgramService = Depends(get_program_service),
    current_user: Annotated[
        CurrentUser,
        Security(get_current_user, scopes=['programs:read'])
    ] = None,
) -> ProgramPublic:
    if current_user is None:
        responses.raise_forbidden()
    try:
        return await service.get_program_by_id(program_id)
    except ValueError as e:
        responses.raise_not_found(detail=str(e))


@router.post(
    '/',
    response_model=ProgramPublic,
    status_code=status.HTTP_201_CREATED,
    responses={
        **responses.auth_responses,
        **responses.bad_request_responses,
        **responses.common_responses,
    }
)
async def create_program(
    program_data: ProgramCreate,
    service: ProgramService = Depends(get_program_service),
    current_user: Annotated[
        CurrentUser,
        Security(get_current_user, scopes=['programs:create'])
    ] = None,
) -> ProgramPublic:
    if current_user is None:
        responses.raise_forbidden()
    try:
        return await service.create_program(program_data, current_user.id)
    except ValueError as e:
        responses.raise_bad_request(str(e))


@router.put(
    '/{program_id}',
    response_model=ProgramPublic,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.bad_request_responses,
        **responses.common_responses,
    }
)
async def update_program(
    program_id: int,
    program_data: ProgramUpdate,
    service: ProgramService = Depends(get_program_service),
    current_user: Annotated[
        CurrentUser,
        Security(get_current_user, scopes=['programs:update'])
    ] = None,
) -> ProgramPublic:
    if current_user is None:
        responses.raise_forbidden()
    try:
        return await service.update_program(program_id, program_data)
    except ValueError as e:
        if 'not found' in str(e):
            responses.raise_not_found(detail=str(e))
        responses.raise_bad_request(str(e))


@router.delete(
    '/{program_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.common_responses,
    }
)
async def delete_program(
    program_id: int,
    service: ProgramService = Depends(get_program_service),
    current_user: Annotated[
        CurrentUser,
        Security(get_current_user, scopes=['programs:delete'])
    ] = None,
) -> None:
    if current_user is None:
        responses.raise_forbidden()
    try:
        await service.delete_program(program_id)
    except ValueError as e:
        responses.raise_not_found(detail=str(e))


@router.post(
    '/{program_id}/copy',
    response_model=ProgramPublic,
    status_code=status.HTTP_201_CREATED,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.bad_request_responses,
        **responses.common_responses,
    }
)
async def copy_program(
    program_id: int,
    copy_request: ProgramCopyRequest,
    service: ProgramService = Depends(get_program_service),
    current_user: Annotated[
        CurrentUser,
        Security(get_current_user, scopes=['programs:create'])
    ] = None,
) -> ProgramPublic:
    if current_user is None:
        responses.raise_forbidden()
    try:
        return await service.copy_program(program_id, copy_request, current_user.id)
    except ValueError as e:
        if 'not found' in str(e):
            responses.raise_not_found(detail=str(e))
        responses.raise_bad_request(str(e))