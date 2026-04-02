from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_user_service
from app.schemas.base import PaginatedResponse
from app.schemas.user import UserPublic, UserUpdate
from app.services.user import UserService

router = APIRouter(prefix='/users', tags=['users'])


@router.get(
    '/',
    response_model=PaginatedResponse[UserPublic],
    summary='Получить список пользователей',
)
async def get_users(
    role: str = None,
    skip: int = 0,
    limit: int = 20,
    user_service: UserService = Depends(get_user_service),
) -> PaginatedResponse[UserPublic]:
    """Получить список пользователей с пагинацией и фильтрацией по роли."""
    return await user_service.get_users(role, skip, limit)


@router.get(
    '/{user_id}',
    response_model=UserPublic,
    summary='Получить пользователя по ID',
)
async def get_user_by_id(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
) -> UserPublic:
    """Получить информацию о пользователе по ID."""
    try:
        return await user_service.get_user_by_id(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put(
    '/me',
    response_model=UserPublic,
    summary='Обновить свой профиль',
)
async def update_own_profile(
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
) -> UserPublic:
    """Обновить данные своего профиля (только имя и фамилия)."""
    try:
        # TODO: В будущем брать current_user.id из токена
        dummy_user_id = 1
        return await user_service.update_own_profile(dummy_user_id, user_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put(
    '/{user_id}',
    response_model=UserPublic,
    summary='Обновить пользователя (админ)',
)
async def update_user_by_admin(
    user_id: int,
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
) -> UserPublic:
    """Обновить данные пользователя. Требует прав администратора."""
    try:
        return await user_service.update_user_by_admin(user_id, user_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
