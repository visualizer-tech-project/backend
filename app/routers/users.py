from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, Security, Query
from pydantic import BaseModel

from app.core import responses
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
    if current_user is None:
        responses.raise_forbidden()
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
    if current_user is None:
        responses.raise_forbidden()
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
    if current_user is None:
        responses.raise_forbidden()
    user = await user_service.get_user_by_id(user_id)
    if user is None:
        responses.raise_not_found('User')
    return user


@router.put('/me')
async def update_own_profile(
    user_data: UserUpdate,
    current_user: Annotated[
        CurrentUser,
        Security(get_current_user, scopes=['profile:update'])
    ],
    user_service: UserService = Depends(get_user_service),
) -> UserPublic:
    if current_user is None:
        responses.raise_forbidden()
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
    if current_user is None:
        responses.raise_forbidden()

    user = await user_service.get_user_by_id(user_id)
    if user is None:
        responses.raise_not_found('User')

    role = await role_service.get_role_by_name(request.role_name)
    if role is None:
        responses.raise_not_found('Role')

    current_roles = await role_service._role_repository.get_user_roles(user_id)
    current_role_ids = [r.id for r in current_roles]

    if role.id not in current_role_ids:
        current_role_ids.append(role.id)

    await role_service.assign_roles_to_user(user_id, current_role_ids)

    return user
