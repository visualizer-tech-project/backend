from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_progress_service
from app.models.base import PaginatedResponse
from app.models.filters import ProgressFilters
from app.models.userprogress import (
    ProgressCreate,
    ProgressUpdate,
    UserProgressPublic,
    UserProgressWithDetails,
)
from app.services.progress import ProgressService

router = APIRouter(prefix='/users', tags=['progress'])


@router.get('/{user_id}/progress', response_model=PaginatedResponse[UserProgressWithDetails])
async def get_user_progress(
    user_id: int,
    filters: ProgressFilters = Depends(),
    service: ProgressService = Depends(get_progress_service),
) -> PaginatedResponse[UserProgressWithDetails]:
    try:
        return await service.get_user_progress(user_id, filters)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post('/{user_id}/courses/{course_id}/progress', response_model=UserProgressPublic, status_code=status.HTTP_201_CREATED)
async def create_progress(
    user_id: int,
    course_id: int,
    progress_data: ProgressCreate,
    service: ProgressService = Depends(get_progress_service),
) -> UserProgressPublic:
    try:
        return await service.create_progress(user_id, course_id, progress_data)
    except ValueError as e:
        if 'already exists' in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put('/{user_id}/courses/{course_id}/progress', response_model=UserProgressPublic)
async def update_progress(
    user_id: int,
    course_id: int,
    progress_data: ProgressUpdate,
    service: ProgressService = Depends(get_progress_service),
) -> UserProgressPublic:
    try:
        return await service.update_progress(user_id, course_id, progress_data)
    except ValueError as e:
        if 'not found' in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete('/{user_id}/courses/{course_id}/progress', status_code=status.HTTP_204_NO_CONTENT)
async def delete_progress(
    user_id: int,
    course_id: int,
    service: ProgressService = Depends(get_progress_service),
) -> None:
    try:
        await service.delete_progress(user_id, course_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))