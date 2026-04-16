from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, Security, status

from app.core import exceptions, responses
from app.core.security import get_current_user, CurrentUser
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
    }
)
async def get_roles(
        current_user: Annotated[
            CurrentUser,
            Security(get_current_user, scopes=['roles:list'])
        ],
        role_service: RoleService = Depends(get_role_service),
) -> Sequence[Role]:
    if current_user is None:
        raise exceptions.ForbiddenError()
    return await role_service.get_roles()


@router.get(
    '/{role_id}',
    response_model=RolePublic,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.common_responses,
    }
)
async def get_role(
        role_id: int,
        current_user: Annotated[
            CurrentUser,
            Security(get_current_user, scopes=['roles:read'])
        ],
        role_service: RoleService = Depends(get_role_service),
) -> Role:
    if current_user is None:
        raise exceptions.ForbiddenError()

    role = await role_service.get_role_by_id(role_id)
    if role is None:
        raise exceptions.NotFoundError('Role')
    return role


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=RolePublic,
    responses={
        **responses.auth_responses,
        **responses.common_responses,
    }
)
async def create_role(
        role_data: RoleCreate,
        current_user: Annotated[
            CurrentUser,
            Security(get_current_user, scopes=['roles:create'])
        ],
        role_service: RoleService = Depends(get_role_service),
) -> Role:
    if current_user is None:
        raise exceptions.ForbiddenError()
    return await role_service.create_role(role_data)


@router.put(
    '/{role_id}',
    response_model=RolePublic,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.common_responses,
    }
)
async def update_role(
        role_id: int,
        role_data: RoleUpdate,
        current_user: Annotated[
            CurrentUser,
            Security(get_current_user, scopes=['roles:update'])
        ],
        role_service: RoleService = Depends(get_role_service),
) -> Role:
    if current_user is None:
        raise exceptions.ForbiddenError()

    role = await role_service.update_role(role_id, role_data)
    if role is None:
        raise exceptions.NotFoundError('Role')
    return role


@router.delete(
    '/{role_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.common_responses,
    }
)
async def delete_role(
        role_id: int,
        current_user: Annotated[
            CurrentUser,
            Security(get_current_user, scopes=['roles:delete'])
        ],
        role_service: RoleService = Depends(get_role_service),
) -> None:
    if current_user is None:
        raise exceptions.ForbiddenError()

    deleted = await role_service.delete_role(role_id)
    if not deleted:
        raise exceptions.NotFoundError('Role')