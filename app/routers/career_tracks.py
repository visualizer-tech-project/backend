from fastapi import APIRouter, Depends, HTTPException, status, Security

from app.models.user import User
from app.schemas.careertrack import (
    CareerTrackCreate,
    CareerTrackUpdate,
    CareerTrackPublic,
    AddCourseToTrack,
    TrackCourseItem,
)
from app.schemas.base import PaginatedResponse
from app.services.careertrack import CareerTrackService
from app.dependencies import (
    get_career_track_service,
    require_write_career_tracks,
    require_delete_career_tracks,
)

router = APIRouter(prefix="/career-tracks", tags=["career-tracks"])


@router.get(
    "/",
    response_model=PaginatedResponse[CareerTrackPublic],
    summary="Получить список карьерных треков",
    responses={
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def get_tracks(
    program_id: int = None,
    title: str = None,
    skip: int = 0,
    limit: int = 20,
    track_service: CareerTrackService = Depends(get_career_track_service),
) -> PaginatedResponse[CareerTrackPublic]:
    """Получить список карьерных треков с пагинацией и фильтрацией."""
    return await track_service.get_tracks(program_id, title, skip, limit)


@router.get(
    "/{track_id}",
    response_model=CareerTrackPublic,
    summary="Получить карьерный трек по ID",
    responses={
        404: {"description": "Трек не найден"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
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
    "/{track_id}/courses",
    response_model=list[TrackCourseItem],
    summary="Получить курсы в карьерном треке",
    responses={
        404: {"description": "Трек не найден"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def get_track_courses(
    track_id: int,
    track_service: CareerTrackService = Depends(get_career_track_service),
) -> list[TrackCourseItem]:
    """Получить список курсов с порядковыми номерами в карьерном треке."""
    try:
        return await track_service.get_track_courses(track_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/",
    response_model=CareerTrackPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый карьерный трек",
    responses={
        400: {"description": "Некорректные данные или program_id не существует"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def create_track(
    track_data: CareerTrackCreate,
    track_service: CareerTrackService = Depends(get_career_track_service),
    current_user: User = Security(require_write_career_tracks, scopes=["write:career-tracks"]),
) -> CareerTrackPublic:
    """Создать новый карьерный трек."""
    try:
        return await track_service.create_track(track_data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put(
    "/{track_id}",
    response_model=CareerTrackPublic,
    summary="Обновить карьерный трек",
    responses={
        400: {"description": "Некорректные данные"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав"},
        404: {"description": "Трек не найден"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def update_track(
    track_id: int,
    track_data: CareerTrackUpdate,
    track_service: CareerTrackService = Depends(get_career_track_service),
    current_user: User = Security(require_write_career_tracks, scopes=["write:career-tracks"]),
) -> CareerTrackPublic:
    """Обновить карьерный трек."""
    try:
        return await track_service.update_track(track_id, track_data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/{track_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить карьерный трек",
    responses={
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав"},
        404: {"description": "Трек не найден"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def delete_track(
    track_id: int,
    track_service: CareerTrackService = Depends(get_career_track_service),
    current_user: User = Security(require_delete_career_tracks, scopes=["delete:career-tracks"]),
) -> None:
    """Удалить карьерный трек."""
    try:
        await track_service.delete_track(track_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/{track_id}/courses",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить курс в карьерный трек",
    responses={
        400: {"description": "Некорректные данные или курс уже в треке"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав"},
        404: {"description": "Трек или курс не найдены"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def add_course_to_track(
    track_id: int,
    add_data: AddCourseToTrack,
    track_service: CareerTrackService = Depends(get_career_track_service),
    current_user: User = Security(require_write_career_tracks, scopes=["write:career-tracks"]),
) -> dict:
    """Добавить курс в карьерный трек с указанием порядка."""
    try:
        return await track_service.add_course_to_track(track_id, add_data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{track_id}/courses/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить курс из карьерного трека",
    responses={
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав"},
        404: {"description": "Связь не найдена"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
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
