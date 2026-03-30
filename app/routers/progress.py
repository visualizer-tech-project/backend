from fastapi import APIRouter, Depends, HTTPException, status, Security

from app.models.user import User
from app.schemas.userprogress import (
    ProgressCreate,
    ProgressUpdate,
    UserProgressPublic,
    UserProgressWithDetails,
    ProgressStatus,
)
from app.schemas.base import PaginatedResponse
from app.services.progress import ProgressService
from app.dependencies import (
    get_progress_service,
    get_current_active_user,
    require_write_users,
)

router = APIRouter(prefix="/users", tags=["progress"])


@router.get(
    "/{user_id}/progress",
    response_model=PaginatedResponse[UserProgressWithDetails],
    summary="Получить прогресс пользователя по курсам",
    responses={
        401: {"description": "Не авторизован"},
        403: {"description": "Нет доступа к прогрессу этого пользователя"},
        404: {"description": "Пользователь не найден"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def get_user_progress(
    user_id: int,
    status: ProgressStatus = None,
    program_id: int = None,
    skip: int = 0,
    limit: int = 20,
    progress_service: ProgressService = Depends(get_progress_service),
    current_user: User = Security(get_current_active_user, scopes=["read:users"]),
) -> PaginatedResponse[UserProgressWithDetails]:
    """Получить прогресс пользователя по курсам с фильтрацией."""
    try:
        return await progress_service.get_user_progress(
            user_id, current_user, status, program_id, skip, limit
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/{user_id}/courses/{course_id}/progress",
    response_model=UserProgressPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Отметить прогресс по курсу для пользователя",
    responses={
        400: {"description": "Некорректные данные или запись уже существует"},
        401: {"description": "Не авторизован"},
        403: {"description": "Нет прав для отметки прогресса этому пользователю"},
        404: {"description": "Пользователь или курс не найдены"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def create_progress(
    user_id: int,
    course_id: int,
    progress_data: ProgressCreate,
    progress_service: ProgressService = Depends(get_progress_service),
    current_user: User = Security(require_write_users, scopes=["write:users"]),
) -> UserProgressPublic:
    """Отметить прогресс по курсу для пользователя."""
    try:
        return await progress_service.create_progress(
            user_id, course_id, progress_data, current_user
        )
    except ValueError as e:
        if "already exists" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put(
    "/{user_id}/courses/{course_id}/progress",
    response_model=UserProgressPublic,
    summary="Обновить прогресс по курсу для пользователя",
    responses={
        400: {"description": "Некорректные данные"},
        401: {"description": "Не авторизован"},
        403: {"description": "Нет прав для обновления прогресса этого пользователя"},
        404: {"description": "Запись прогресса не найдена"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def update_progress(
    user_id: int,
    course_id: int,
    progress_data: ProgressUpdate,
    progress_service: ProgressService = Depends(get_progress_service),
    current_user: User = Security(require_write_users, scopes=["write:users"]),
) -> UserProgressPublic:
    """Обновить прогресс по курсу для пользователя."""
    try:
        return await progress_service.update_progress(
            user_id, course_id, progress_data, current_user
        )
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete(
    "/{user_id}/courses/{course_id}/progress",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить запись о прогрессе пользователя по курсу",
    responses={
        401: {"description": "Не авторизован"},
        403: {"description": "Нет прав для удаления прогресса этого пользователя"},
        404: {"description": "Запись не найдена"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def delete_progress(
    user_id: int,
    course_id: int,
    progress_service: ProgressService = Depends(get_progress_service),
    current_user: User = Security(require_write_users, scopes=["write:users"]),
) -> None:
    """Удалить запись о прогрессе пользователя по курсу."""
    try:
        await progress_service.delete_progress(user_id, course_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
