from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_progress_service
from app.schemas.base import PaginatedResponse
from app.schemas.userprogress import (
    ProgressCreate,
    ProgressStatus,
    ProgressUpdate,
    UserProgressPublic,
    UserProgressWithDetails,
)
from app.services.progress import ProgressService

router = APIRouter(prefix='/users', tags=['progress'])


@router.get(
    '/{user_id}/progress',
    response_model=PaginatedResponse[UserProgressWithDetails],
    summary='Получить прогресс пользователя по курсам',
)
async def get_user_progress(
    user_id: int,
    status: ProgressStatus = None,
    program_id: int = None,
    skip: int = 0,
    limit: int = 20,
    progress_service: ProgressService = Depends(get_progress_service),
) -> PaginatedResponse[UserProgressWithDetails]:
    """Получить прогресс пользователя по курсам с фильтрацией."""
    try:
        return await progress_service.get_user_progress(
            user_id, status, program_id, skip, limit
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    '/{user_id}/courses/{course_id}/progress',
    response_model=UserProgressPublic,
    status_code=status.HTTP_201_CREATED,
    summary='Отметить прогресс по курсу для пользователя',
)
async def create_progress(
    user_id: int,
    course_id: int,
    progress_data: ProgressCreate,
    progress_service: ProgressService = Depends(get_progress_service),
) -> UserProgressPublic:
    """Отметить прогресс по курсу для пользователя."""
    try:
        return await progress_service.create_progress(user_id, course_id, progress_data)
    except ValueError as e:
        if 'already exists' in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put(
    '/{user_id}/courses/{course_id}/progress',
    response_model=UserProgressPublic,
    summary='Обновить прогресс по курсу для пользователя',
)
async def update_progress(
    user_id: int,
    course_id: int,
    progress_data: ProgressUpdate,
    progress_service: ProgressService = Depends(get_progress_service),
) -> UserProgressPublic:
    """Обновить прогресс по курсу для пользователя."""
    try:
        return await progress_service.update_progress(user_id, course_id, progress_data)
    except ValueError as e:
        if 'not found' in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    '/{user_id}/courses/{course_id}/progress',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Удалить запись о прогрессе пользователя по курсу',
)
async def delete_progress(
    user_id: int,
    course_id: int,
    progress_service: ProgressService = Depends(get_progress_service),
) -> None:
    """Удалить запись о прогрессе пользователя по курсу."""
    try:
        await progress_service.delete_progress(user_id, course_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
