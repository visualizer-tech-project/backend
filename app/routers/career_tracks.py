from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_career_track_service
from app.models.user import User
from app.schemas.base import PaginatedResponse
from app.schemas.careertrack import (
    AddCourseToTrack,
    CareerTrackCoursePublic,
    CareerTrackCreate,
    CareerTrackPublic,
    CareerTrackUpdate,
    TrackCourseItem,
)
from app.services.careertrack import CareerTrackService

# Временная заглушка для текущего пользователя
DUMMY_USER = User(id=1, role='admin')

router = APIRouter(prefix='/career-tracks', tags=['career-tracks'])


@router.get(
    '/',
    response_model=PaginatedResponse[CareerTrackPublic],
    summary='Получить список карьерных треков',
)
async def get_tracks(
    title: str = None,
    skip: int = 0,
    limit: int = 20,
    track_service: CareerTrackService = Depends(get_career_track_service),
) -> PaginatedResponse[CareerTrackPublic]:
    """Получить список карьерных треков с пагинацией и фильтрацией."""
    return await track_service.get_tracks(title, skip, limit)


@router.get(
    '/{track_id}',
    response_model=CareerTrackPublic,
    summary='Получить карьерный трек по ID',
)
async def get_track_by_id(
    track_id: int,
    track_service: CareerTrackService = Depends(get_career_track_service),
) -> CareerTrackPublic:
    """Получить информацию о карьерном треке по ID."""
    try:
        return await track_service.get_track_by_id(track_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    '/{track_id}/courses',
    response_model=list[TrackCourseItem],
    summary='Получить курсы в карьерном треке',
)
async def get_track_courses(
    track_id: int,
    skip: int = 0,
    limit: int = 100,
    track_service: CareerTrackService = Depends(get_career_track_service),
) -> list[TrackCourseItem]:
    """Получить список курсов с порядковыми номерами в карьерном треке."""
    try:
        return await track_service.get_track_courses(track_id, skip, limit)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    '/',
    response_model=CareerTrackPublic,
    status_code=status.HTTP_201_CREATED,
    summary='Создать новый карьерный трек',
)
async def create_track(
    track_data: CareerTrackCreate,
    track_service: CareerTrackService = Depends(get_career_track_service),
) -> CareerTrackPublic:
    """Создать новый карьерный трек."""
    try:
        return await track_service.create_track(track_data, DUMMY_USER)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put(
    '/{track_id}',
    response_model=CareerTrackPublic,
    summary='Обновить карьерный трек',
)
async def update_track(
    track_id: int,
    track_data: CareerTrackUpdate,
    track_service: CareerTrackService = Depends(get_career_track_service),
) -> CareerTrackPublic:
    """Обновить карьерный трек."""
    try:
        return await track_service.update_track(track_id, track_data, DUMMY_USER)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    '/{track_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Удалить карьерный трек',
)
async def delete_track(
    track_id: int,
    track_service: CareerTrackService = Depends(get_career_track_service),
) -> None:
    """Удалить карьерный трек."""
    try:
        await track_service.delete_track(track_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    '/{track_id}/courses',
    response_model=CareerTrackCoursePublic,
    status_code=status.HTTP_201_CREATED,
    summary='Добавить курс в карьерный трек',
)
async def add_course_to_track(
    track_id: int,
    add_data: AddCourseToTrack,
    track_service: CareerTrackService = Depends(get_career_track_service),
) -> CareerTrackCoursePublic:
    """Добавить курс в карьерный трек с указанием порядка."""
    try:
        return await track_service.add_course_to_track(track_id, add_data, DUMMY_USER)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    '/{track_id}/courses/{course_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Удалить курс из карьерного трека',
)
async def remove_course_from_track(
    track_id: int,
    course_id: int,
    track_service: CareerTrackService = Depends(get_career_track_service),
) -> None:
    """Удалить курс из карьерного трека."""
    try:
        await track_service.remove_course_from_track(track_id, course_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
