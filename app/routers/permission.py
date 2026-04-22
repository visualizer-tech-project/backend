from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, Security

from app.core import responses
from app.core.security import get_current_user, CurrentUser
from app.dependencies.services import get_permission_service
from app.models.permission import PermissionPublic
from app.services.permission import PermissionService

router = APIRouter(prefix='/permissions', tags=['permissions'])


@router.get(
    '/',
    response_model=Sequence[PermissionPublic],
    responses={
        **responses.auth_responses,
        **responses.common_responses,
    }
)
async def get_permissions(
    current_user: Annotated[
        CurrentUser,
        Security(get_current_user, scopes=['permissions:list'])
    ],
    permission_service: PermissionService = Depends(get_permission_service),
) -> Sequence[PermissionPublic]:
    return await permission_service.get_permissions()