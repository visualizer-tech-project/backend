from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_career_track_service
from app.models.base import PaginatedResponse
from app.models.careertrack import (
    AddCourseToTrack,
    CareerTrackCoursePublic,
    CareerTrackCreate,
    CareerTrackPublic,
    CareerTrackUpdate,
    TrackCourseItem,
)
from app.models.filters import CareerTrackFilters
from app.services.careertrack import CareerTrackService

router = APIRouter(prefix='/career-tracks', tags=['career-tracks'])


@router.get('/', response_model=PaginatedResponse[CareerTrackPublic])
async def get_tracks(
    filters: CareerTrackFilters = Depends(),
    service: CareerTrackService = Depends(get_career_track_service),
) -> PaginatedResponse[CareerTrackPublic]:
    return await service.get_tracks(filters)


@router.get('/{track_id}', response_model=CareerTrackPublic)
async def get_track_by_id(
    track_id: int,
    service: CareerTrackService = Depends(get_career_track_service),
) -> CareerTrackPublic:
    try:
        return await service.get_track_by_id(track_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get('/{track_id}/courses', response_model=list[TrackCourseItem])
async def get_track_courses(
    track_id: int,
    skip: int = 0,
    limit: int = 100,
    service: CareerTrackService = Depends(get_career_track_service),
) -> list[TrackCourseItem]:
    try:
        return await service.get_track_courses(track_id, skip, limit)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post('/', response_model=CareerTrackPublic, status_code=status.HTTP_201_CREATED)
async def create_track(
    track_data: CareerTrackCreate,
    service: CareerTrackService = Depends(get_career_track_service),
) -> CareerTrackPublic:
    try:
        return await service.create_track(track_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put('/{track_id}', response_model=CareerTrackPublic)
async def update_track(
    track_id: int,
    track_data: CareerTrackUpdate,
    service: CareerTrackService = Depends(get_career_track_service),
) -> CareerTrackPublic:
    try:
        return await service.update_track(track_id, track_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete('/{track_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_track(
    track_id: int,
    service: CareerTrackService = Depends(get_career_track_service),
) -> None:
    try:
        await service.delete_track(track_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post('/{track_id}/courses', response_model=CareerTrackCoursePublic, status_code=status.HTTP_201_CREATED)
async def add_course_to_track(
    track_id: int,
    add_data: AddCourseToTrack,
    service: CareerTrackService = Depends(get_career_track_service),
) -> CareerTrackCoursePublic:
    try:
        return await service.add_course_to_track(track_id, add_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete('/{track_id}/courses/{course_id}', status_code=status.HTTP_204_NO_CONTENT)
async def remove_course_from_track(
    track_id: int,
    course_id: int,
    service: CareerTrackService = Depends(get_career_track_service),
) -> None:
    try:
        await service.remove_course_from_track(track_id, course_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))