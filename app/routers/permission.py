from typing import Sequence

from fastapi import APIRouter, Depends, Security, Request

from app.core import responses
from app.core.rate_limiter import limiter
from app.core.security import get_current_user
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
    },
    dependencies=[Security(get_current_user, scopes=['permissions:list'])]
)
@limiter.limit("30/minute")
async def get_permissions(
    request: Request,
    permission_service: PermissionService = Depends(get_permission_service),
) -> Sequence[PermissionPublic]:
    return await permission_service.get_permissions()