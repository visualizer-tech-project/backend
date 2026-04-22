from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, Security, Query
from pydantic import BaseModel

from app.core import exceptions, responses
from app.core.security import get_current_user, CurrentUser
from app.dependencies.services import get_user_service, get_role_service
from app.models.user import UserPublic, UserUpdate
from app.schemas.filters import UserFilters
from app.services.user import UserService
from app.services.role import RoleService

router = APIRouter(prefix='/users', tags=['users'])


class EscalateRoleRequest(BaseModel):
    role_name: str


@router.get(
    '/me',
    response_model=UserPublic,
    responses={
        **responses.auth_responses,
        **responses.common_responses,
    }
)
async def get_profile(
    current_user: Annotated[
        CurrentUser,
        Security(get_current_user, scopes=['profile:read'])
    ],
) -> UserPublic:
    return UserPublic.model_validate(current_user)


@router.get(
    '/',
    response_model=Sequence[UserPublic],
    responses={
        **responses.auth_responses,
        **responses.common_responses,
    }
)
async def get_users(
    current_user: Annotated[
        CurrentUser,
        Security(get_current_user, scopes=['profile:list'])
    ],
    user_service: UserService = Depends(get_user_service),
    filters: Annotated[UserFilters, Query()] = Depends(),
) -> Sequence[UserPublic]:
    result = await user_service.get_users(filters)
    return result.items


@router.get(
    '/{user_id}',
    response_model=UserPublic,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.common_responses,
    }
)
async def get_user(
    user_id: int,
    current_user: Annotated[
        CurrentUser,
        Security(get_current_user, scopes=['profile:detail'])
    ],
    user_service: UserService = Depends(get_user_service),
) -> UserPublic:
    return await user_service.get_user_by_id(user_id)


@router.put('/me')
async def update_own_profile(
    user_data: UserUpdate,
    current_user: Annotated[
        CurrentUser,
        Security(get_current_user, scopes=['profile:update'])
    ],
    user_service: UserService = Depends(get_user_service),
) -> UserPublic:
    return await user_service.update_user(current_user.id, user_data)


@router.post(
    '/{user_id}/escalate',
    response_model=UserPublic,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.common_responses,
    }
)
async def escalate_user_role(
    user_id: int,
    request: EscalateRoleRequest,
    current_user: Annotated[
        CurrentUser,
        Security(get_current_user, scopes=['roles:update'])
    ],
    user_service: UserService = Depends(get_user_service),
    role_service: RoleService = Depends(get_role_service),
) -> UserPublic:
    await user_service.get_user_by_id(user_id)

    role = await role_service.get_role_by_name(request.role_name)
    if not role:
        raise exceptions.NotFoundError(f"Role with name {request.role_name} not found")

    current_role_ids = await role_service.get_user_role_ids(user_id)

    if role.id not in current_role_ids:
        current_role_ids.append(role.id)

    await role_service.assign_roles_to_user(user_id, current_role_ids)

    return await user_service.get_user_by_id(user_id)
