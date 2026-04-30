from fastapi import APIRouter, Depends, Security, status, Request

from app.core import exceptions, responses
from app.core.rate_limiter import limiter
from app.core.security import get_current_user
from app.dependencies import get_progress_service, CurrentUser
from app.models.base import ListResponse
from app.schemas.filters import ProgressFilters
from app.models.userprogress import (
    ProgressCreate,
    ProgressUpdate,
    UserProgressPublic,
)
from app.schemas.userprogress import UserProgressWithDetails
from app.services.progress import ProgressService

router = APIRouter(prefix='/users', tags=['progress'])


@router.get(
    '/{user_id}/progress',
    response_model=ListResponse[UserProgressWithDetails],
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.common_responses,
    },
)
@limiter.limit("30/minute")
async def get_user_progress(
    request: Request,
    user_id: int,
    filters: ProgressFilters = Depends(),
    service: ProgressService = Depends(get_progress_service),
    current_user: CurrentUser = Security(get_current_user, scopes=['progress:list']),
) -> ListResponse[UserProgressWithDetails]:

    if current_user.id != user_id:
        if 'progress:view_any' not in current_user.scopes:
            raise exceptions.ForbiddenError('Not enough permissions')

    return await service.get_user_progress(user_id, filters)


@router.post(
    '/{user_id}/courses/{course_id}/progress',
    response_model=UserProgressPublic,
    status_code=status.HTTP_201_CREATED,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.bad_request_responses,
        **responses.conflict_responses,
        **responses.common_responses,
    },
)
@limiter.limit("10/minute")
async def create_progress(
    request: Request,
    user_id: int,
    course_id: int,
    progress_data: ProgressCreate,
    service: ProgressService = Depends(get_progress_service),
    current_user: CurrentUser = Security(get_current_user, scopes=['progress:create']),
) -> UserProgressPublic:
    if current_user.id != user_id:
        if 'progress:modify_any' not in current_user.scopes:
            raise exceptions.ForbiddenError('Not enough permissions')
    progress_data.user_id = user_id
    progress_data.course_id = course_id
    return await service.create_progress(user_id, course_id, progress_data)


@router.put(
    '/{user_id}/courses/{course_id}/progress',
    response_model=UserProgressPublic,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.bad_request_responses,
        **responses.common_responses,
    },
)
@limiter.limit("10/minute")
async def update_progress(
    request: Request,
    user_id: int,
    course_id: int,
    progress_data: ProgressUpdate,
    service: ProgressService = Depends(get_progress_service),
    current_user: CurrentUser = Security(get_current_user, scopes=['progress:update']),
) -> UserProgressPublic:
    if current_user.id != user_id:
        if 'progress:modify_any' not in current_user.scopes:
            raise exceptions.ForbiddenError('Not enough permissions')
    return await service.update_progress(user_id, course_id, progress_data)


@router.delete(
    '/{user_id}/courses/{course_id}/progress',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.common_responses,
    },
)
@limiter.limit("10/minute")
async def delete_progress(
    request: Request,
    user_id: int,
    course_id: int,
    service: ProgressService = Depends(get_progress_service),
    current_user: CurrentUser = Security(get_current_user, scopes=['progress:delete']),
) -> None:
    if current_user.id != user_id:
        if 'progress:modify_any' not in current_user.scopes:
            raise exceptions.ForbiddenError('Not enough permissions')

    await service.delete_progress(user_id, course_id)
