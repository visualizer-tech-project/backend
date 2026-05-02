from typing import Sequence

from fastapi import APIRouter, Depends, Security, status, Request

from app.core import responses
from app.core.rate_limiter import limiter
from app.core.security import get_current_user
from app.dependencies.services import get_role_service
from app.models.role import RolePublic, RoleCreate, RoleUpdate, Role
from app.services.role import RoleService

router = APIRouter(prefix='/roles', tags=['roles'])


@router.get(
    '/',
    response_model=Sequence[RolePublic],
    responses={
        **responses.auth_responses,
        **responses.common_responses,
    },
    dependencies=[Security(get_current_user, scopes=['roles:list'])]
)
@limiter.limit("30/minute")
async def get_roles(
    request: Request,
    role_service: RoleService = Depends(get_role_service),
) -> Sequence[Role]:
    return await role_service.get_roles()


@router.get(
    '/{role_id}',
    response_model=RolePublic,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.common_responses,
    },
    dependencies=[Security(get_current_user, scopes=['roles:read'])]
)
@limiter.limit("30/minute")
async def get_role(
    request: Request,
    role_id: int,
    role_service: RoleService = Depends(get_role_service),
) -> Role:
    return await role_service.get_role_by_id(role_id)


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=RolePublic,
    responses={
        **responses.auth_responses,
        **responses.common_responses,
    },
    dependencies=[Security(get_current_user, scopes=['roles:create'])]
)
@limiter.limit("5/minute")
async def create_role(
    request: Request,
    role_data: RoleCreate,
    role_service: RoleService = Depends(get_role_service),
) -> Role:
    return await role_service.create_role(role_data)


@router.put(
    '/{role_id}',
    response_model=RolePublic,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.common_responses,
    },
    dependencies=[Security(get_current_user, scopes=['roles:update'])]
)
@limiter.limit("5/minute")
async def update_role(
    request: Request,
    role_id: int,
    role_data: RoleUpdate,
    role_service: RoleService = Depends(get_role_service),
) -> Role:
    return await role_service.update_role(role_id, role_data)


@router.delete(
    '/{role_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.common_responses,
    },
    dependencies=[Security(get_current_user, scopes=['roles:delete'])]
)
@limiter.limit("5/minute")
async def delete_role(
    request: Request,
    role_id: int,
    role_service: RoleService = Depends(get_role_service),
) -> None:
    await role_service.delete_role(role_id)
