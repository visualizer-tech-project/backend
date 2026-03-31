from fastapi import APIRouter, Depends, HTTPException, status, Security

from app.models.user import User
from app.schemas.user import UserPublic, UserUpdate
from app.schemas.base import PaginatedResponse
from app.services.user import UserService
from app.dependencies import (
    get_user_service,
    get_current_active_user,
    require_admin,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    response_model=PaginatedResponse[UserPublic],
    summary="Получить список пользователей",
    responses={
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
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
    "/{user_id}",
    response_model=UserPublic,
    summary="Получить пользователя по ID",
    responses={
        401: {"description": "Не авторизован"},
        403: {"description": "Нет доступа к данному пользователю"},
        404: {"description": "Пользователь не найден"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
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
    "/{user_id}",
    response_model=UserPublic,
    summary="Обновить данные пользователя",
    responses={
        400: {"description": "Некорректные данные"},
        401: {"description": "Не авторизован"},
        403: {"description": "Нет прав на редактирование"},
        404: {"description": "Пользователь не найден"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Security(get_current_active_user, scopes=["write:users"]),
) -> UserPublic:
    """Обновить данные пользователя."""
    try:
        return await user_service.update_user(user_id, user_data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/{user_id}/assign-teacher",
    response_model=UserPublic,
    summary="Назначить роль преподавателя",
    description="Изменяет роль пользователя с 'student' на 'teacher'",
    responses={
        400: {"description": "Пользователь уже является преподавателем или администратором"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав"},
        404: {"description": "Пользователь не найден"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def assign_teacher_role(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Security(require_admin, scopes=["admin:assign-teacher"]),
) -> UserPublic:
    """Назначить пользователю роль преподавателя. Только для администраторов."""
    try:
        return await user_service.assign_teacher_role(user_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
