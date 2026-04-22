from typing import Annotated

from fastapi import APIRouter, Depends, Security, status

from app.core import exceptions, responses
from app.core.security import get_current_user, CurrentUser
from app.dependencies import get_progress_service
from app.dependencies.services import get_role_service
from app.models.base import ListResponse
from app.schemas.filters import ProgressFilters
from app.models.userprogress import (
    ProgressCreate,
    ProgressUpdate,
    UserProgressPublic,
)
from app.schemas.userprogress import UserProgressWithDetails
from app.services.progress import ProgressService
from app.services.role import RoleService

router = APIRouter(prefix='/users', tags=['progress'])


@router.get(
    '/{user_id}/progress',
    response_model=ListResponse[UserProgressWithDetails],
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.common_responses,
    }
)
async def get_user_progress(
    user_id: int,
    filters: ProgressFilters = Depends(),
    service: ProgressService = Depends(get_progress_service),
    role_service: RoleService = Depends(get_role_service),
    current_user: Annotated[
        CurrentUser,
        Security(get_current_user, scopes=['progress:list'])
    ] = None,
) -> ListResponse[UserProgressWithDetails]:
    if not await role_service.can_view_user_progress(current_user, user_id):
        raise exceptions.ForbiddenError('You can only view your own progress')
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
    }
)
async def create_progress(
    user_id: int,
    course_id: int,
    progress_data: ProgressCreate,
    service: ProgressService = Depends(get_progress_service),
    role_service: RoleService = Depends(get_role_service),
    current_user: Annotated[
        CurrentUser,
        Security(get_current_user, scopes=['progress:create'])
    ] = None,
) -> UserProgressPublic:
    if not await role_service.can_modify_user_progress(current_user, user_id):
        raise exceptions.ForbiddenError('You can only create progress for yourself')

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
    }
)
async def update_progress(
    user_id: int,
    course_id: int,
    progress_data: ProgressUpdate,
    service: ProgressService = Depends(get_progress_service),
    role_service: RoleService = Depends(get_role_service),
    current_user: Annotated[
        CurrentUser,
        Security(get_current_user, scopes=['progress:update'])
    ] = None,
) -> UserProgressPublic:
    if not await role_service.can_modify_user_progress(current_user, user_id):
        raise exceptions.ForbiddenError('You can only update your own progress')
    return await service.update_progress(user_id, course_id, progress_data)


@router.delete(
    '/{user_id}/courses/{course_id}/progress',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.common_responses,
    }
)
async def delete_progress(
    user_id: int,
    course_id: int,
    service: ProgressService = Depends(get_progress_service),
    role_service: RoleService = Depends(get_role_service),
    current_user: Annotated[
        CurrentUser,
        Security(get_current_user, scopes=['progress:delete'])
    ] = None,
) -> None:
    if not await role_service.can_modify_user_progress(current_user, user_id):
        raise exceptions.ForbiddenError('You can only delete your own progress')
    await service.delete_progress(user_id, course_id)
