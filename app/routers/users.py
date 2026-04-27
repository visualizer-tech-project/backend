from typing import Sequence

from fastapi import APIRouter, Depends, Security, Request
from pydantic import BaseModel

from app.core import exceptions, responses
from app.core.rate_limiter import limiter
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
    },
    dependencies=[Security(get_current_user, scopes=['profile:read'])]
)
@limiter.limit("30/minute")
async def get_profile(
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
) -> UserPublic:
    return UserPublic.model_validate(current_user)


@router.get(
    '/',
    response_model=Sequence[UserPublic],
    responses={
        **responses.auth_responses,
        **responses.common_responses,
    },
    dependencies=[Security(get_current_user, scopes=['profile:list'])]
)
@limiter.limit("30/minute")
async def get_users(
    request: Request,
    user_service: UserService = Depends(get_user_service),
    filters: UserFilters = Depends(),
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
    },
    dependencies=[Security(get_current_user, scopes=['profile:detail'])]
)
@limiter.limit("30/minute")
async def get_user(
    request: Request,
    user_id: int,
    user_service: UserService = Depends(get_user_service),
) -> UserPublic:
    return await user_service.get_user_by_id(user_id)


@router.put(
    '/me',
    response_model=UserPublic,
    responses={
        **responses.auth_responses,
        **responses.common_responses,
    },
    dependencies=[Security(get_current_user, scopes=['profile:update'])]
)
@limiter.limit("10/minute")
async def update_own_profile(
    request: Request,
    user_data: UserUpdate,
    current_user: CurrentUser = Depends(get_current_user),
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
    },
    dependencies=[Security(get_current_user, scopes=['roles:update'])]
)
@limiter.limit("5/minute")
async def escalate_user_role(
    request: Request,
    user_id: int,
    escalate_data: EscalateRoleRequest,
    user_service: UserService = Depends(get_user_service),
    role_service: RoleService = Depends(get_role_service),
) -> UserPublic:
    await user_service.get_user_by_id(user_id)

    role = await role_service.get_role_by_name(escalate_data.role_name)
    if not role:
        raise exceptions.NotFoundError(f"Role with name {escalate_data.role_name} not found")

    current_role_ids = await role_service.get_user_role_ids(user_id)

    if role.id not in current_role_ids:
        current_role_ids.append(role.id)

    await role_service.assign_roles_to_user(user_id, current_role_ids)

    return await user_service.get_user_by_id(user_id)