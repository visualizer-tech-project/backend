from fastapi import APIRouter, Depends, Security, status, Request

from app.core import responses
from app.core.rate_limiter import limiter
from app.core.security import get_current_user, CurrentUser
from app.dependencies import get_career_track_service
from app.models.base import ListResponse
from app.models.careertrack import (
    CareerTrackCreate,
    CareerTrackPublic,
    CareerTrackUpdate,
    CareerTrackCoursePublic,
    TrackCourseItem,
)
from app.schemas.careertrack import AddCourseToTrack
from app.schemas.filters import CareerTrackFilters
from app.services.careertrack import CareerTrackService
from app.core.constants import DEFAULT_SKIP, DEFAULT_LIMIT

router = APIRouter(prefix='/career-tracks', tags=['career-tracks'])


@router.get(
    '/',
    response_model=ListResponse[CareerTrackPublic],
    responses={
        **responses.auth_responses,
        **responses.common_responses,
    },
    dependencies=[Security(get_current_user, scopes=['career_tracks:list'])]
)
@limiter.limit("60/minute")
async def get_tracks(
    request: Request,
    filters: CareerTrackFilters = Depends(),
    service: CareerTrackService = Depends(get_career_track_service),
) -> ListResponse[CareerTrackPublic]:
    return await service.get_tracks(filters)


@router.get(
    '/{track_id}',
    response_model=CareerTrackPublic,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.common_responses,
    },
    dependencies=[Security(get_current_user, scopes=['career_tracks:read'])]
)
@limiter.limit("60/minute")
async def get_track_by_id(
    request: Request,
    track_id: int,
    service: CareerTrackService = Depends(get_career_track_service),
) -> CareerTrackPublic:
    return await service.get_track_by_id(track_id)


@router.get(
    '/{track_id}/courses',
    response_model=list[TrackCourseItem],
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.common_responses,
    },
    dependencies=[Security(get_current_user, scopes=['career_tracks:read'])]
)
@limiter.limit("60/minute")
async def get_track_courses(
    request: Request,
    track_id: int,
    skip: int = DEFAULT_SKIP,
    limit: int = DEFAULT_LIMIT,
    service: CareerTrackService = Depends(get_career_track_service),
) -> list[TrackCourseItem]:
    return await service.get_track_courses(track_id, skip, limit)


@router.post(
    '/',
    response_model=CareerTrackPublic,
    status_code=status.HTTP_201_CREATED,
    responses={
        **responses.auth_responses,
        **responses.bad_request_responses,
        **responses.common_responses,
    },
)
@limiter.limit("10/minute")
async def create_track(
    request: Request,
    track_data: CareerTrackCreate,
    service: CareerTrackService = Depends(get_career_track_service),
    current_user: CurrentUser = Security(get_current_user, scopes=['career_tracks:create']),
) -> CareerTrackPublic:
    current_user = request.user
    return await service.create_track(track_data, current_user.id)


@router.put(
    '/{track_id}',
    response_model=CareerTrackPublic,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.bad_request_responses,
        **responses.common_responses,
    },
    dependencies=[Security(get_current_user, scopes=['career_tracks:update'])]
)
@limiter.limit("10/minute")
async def update_track(
    request: Request,
    track_id: int,
    track_data: CareerTrackUpdate,
    service: CareerTrackService = Depends(get_career_track_service),
) -> CareerTrackPublic:
    return await service.update_track(track_id, track_data)


@router.delete(
    '/{track_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.common_responses,
    },
    dependencies=[Security(get_current_user, scopes=['career_tracks:delete'])]
)
@limiter.limit("10/minute")
async def delete_track(
    request: Request,
    track_id: int,
    service: CareerTrackService = Depends(get_career_track_service),
) -> None:
    await service.delete_track(track_id)


@router.post(
    '/{track_id}/courses',
    response_model=CareerTrackCoursePublic,
    status_code=status.HTTP_201_CREATED,
    responses={
        **responses.auth_responses,
        **responses.bad_request_responses,
        **responses.common_responses,
    },
    dependencies=[Security(get_current_user, scopes=['career_tracks:update'])]
)
@limiter.limit("10/minute")
async def add_course_to_track(
    request: Request,
    track_id: int,
    add_data: AddCourseToTrack,
    service: CareerTrackService = Depends(get_career_track_service),
) -> CareerTrackCoursePublic:
    return await service.add_course_to_track(track_id, add_data)


@router.delete(
    '/{track_id}/courses/{course_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.common_responses,
    },
    dependencies=[Security(get_current_user, scopes=['career_tracks:update'])]
)
@limiter.limit("10/minute")
async def remove_course_from_track(
    request: Request,
    track_id: int,
    course_id: int,
    service: CareerTrackService = Depends(get_career_track_service),
) -> None:
    await service.remove_course_from_track(track_id, course_id)
