from fastapi import APIRouter, Depends, Security, status, Request

from app.core import responses
from app.core.rate_limiter import limiter
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
    },
    dependencies=[Security(get_current_user, scopes=['programs:list'])]
)
@limiter.limit("60/minute")
async def get_programs(
    request: Request,
    filters: ProgramFilters = Depends(),
    service: ProgramService = Depends(get_program_service),
) -> ListResponse[ProgramPublic]:
    return await service.get_programs(filters)


@router.get(
    '/{program_id}',
    response_model=ProgramPublic,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.common_responses,
    },
    dependencies=[Security(get_current_user, scopes=['programs:read'])]
)
@limiter.limit("60/minute")
async def get_program_by_id(
    request: Request,
    program_id: int,
    service: ProgramService = Depends(get_program_service),
) -> ProgramPublic:
    return await service.get_program_by_id(program_id)


@router.post(
    '/',
    response_model=ProgramPublic,
    status_code=status.HTTP_201_CREATED,
    responses={
        **responses.auth_responses,
        **responses.bad_request_responses,
        **responses.common_responses,
    },
)
@limiter.limit("10/minute")
async def create_program(
    request: Request,
    program_data: ProgramCreate,
    service: ProgramService = Depends(get_program_service),
    current_user: CurrentUser = Security(get_current_user, scopes=['programs:create']),
) -> ProgramPublic:
    current_user = request.user
    return await service.create_program(program_data, current_user.id)


@router.put(
    '/{program_id}',
    response_model=ProgramPublic,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.bad_request_responses,
        **responses.common_responses,
    },
    dependencies=[Security(get_current_user, scopes=['programs:update'])]
)
@limiter.limit("10/minute")
async def update_program(
    request: Request,
    program_id: int,
    program_data: ProgramUpdate,
    service: ProgramService = Depends(get_program_service),
) -> ProgramPublic:
    return await service.update_program(program_id, program_data)


@router.delete(
    '/{program_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.common_responses,
    },
    dependencies=[Security(get_current_user, scopes=['programs:delete'])]
)
@limiter.limit("10/minute")
async def delete_program(
    request: Request,
    program_id: int,
    service: ProgramService = Depends(get_program_service),
) -> None:
    await service.delete_program(program_id)


@router.post(
    '/{program_id}/copy',
    response_model=ProgramPublic,
    status_code=status.HTTP_201_CREATED,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.bad_request_responses,
        **responses.common_responses,
    },
)
@limiter.limit("5/minute")
async def copy_program(
    request: Request,
    program_id: int,
    copy_request: ProgramCopyRequest,
    service: ProgramService = Depends(get_program_service),
    current_user: CurrentUser = Security(get_current_user, scopes=['programs:create']),
) -> ProgramPublic:
    current_user = request.user
    return await service.copy_program(program_id, copy_request, current_user.id)
