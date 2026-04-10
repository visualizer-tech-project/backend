from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_user_service
from app.models.base import ListResponse
from app.models.user import UserPublic, UserUpdate
from app.schemas.filters import UserFilters
from app.services.user import UserService

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/', response_model=ListResponse[UserPublic])
async def get_users(
    filters: UserFilters = Depends(),
    service: UserService = Depends(get_user_service),
) -> ListResponse[UserPublic]:
    return await service.get_users(filters)


@router.get('/{user_id}', response_model=UserPublic)
async def get_user_by_id(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> UserPublic:
    try:
        return await service.get_user_by_id(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put('/me', response_model=UserPublic)
async def update_own_profile(
    user_data: UserUpdate,
    service: UserService = Depends(get_user_service),
) -> UserPublic:
    try:
        return await service.update_own_profile(user_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put('/{user_id}', response_model=UserPublic)
async def update_user_by_admin(
    user_id: int,
    user_data: UserUpdate,
    service: UserService = Depends(get_user_service),
) -> UserPublic:
    try:
        return await service.update_user_by_admin(user_id, user_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post('/{user_id}/assign-teacher', response_model=UserPublic, status_code=status.HTTP_200_OK)
async def assign_teacher(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> UserPublic:
    try:
        return await service.assign_teacher(user_id)
    except ValueError as e:
        if 'already' in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
