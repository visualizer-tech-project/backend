from fastapi import APIRouter, Depends, Security, status, Request

from app.core import responses
from app.core.rate_limiter import limiter
from app.dependencies import CurrentUser, get_current_user
from app.dependencies import get_course_service
from app.models.base import ListResponse
from app.models.course import CourseCreate, CoursePublic, CourseUpdate
from app.models.prerequisite import PrerequisiteCreate, PrerequisitePublic
from app.schemas.filters import CourseFilters
from app.services.course import CourseService

router = APIRouter(prefix='/courses', tags=['courses'])


@router.get(
    '/',
    response_model=ListResponse[CoursePublic],
    responses={
        **responses.auth_responses,
        **responses.common_responses,
    },
    dependencies=[Security(get_current_user, scopes=['courses:list'])]
)
@limiter.limit("60/minute")
async def get_courses(
    request: Request,
    filters: CourseFilters = Depends(),
    service: CourseService = Depends(get_course_service),
) -> ListResponse[CoursePublic]:
    return await service.get_courses(filters)


@router.get(
    '/{course_id}',
    response_model=CoursePublic,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.common_responses,
    },
    dependencies=[Security(get_current_user, scopes=['courses:read'])]
)
@limiter.limit("60/minute")
async def get_course_by_id(
    request: Request,
    course_id: int,
    service: CourseService = Depends(get_course_service),
) -> CoursePublic:
    return await service.get_course_by_id(course_id)


@router.post(
    '/',
    response_model=CoursePublic,
    status_code=status.HTTP_201_CREATED,
    responses={
        **responses.auth_responses,
        **responses.bad_request_responses,
        **responses.common_responses,
    },
)
@limiter.limit("10/minute")
async def create_course(
    request: Request,
    course_data: CourseCreate,
    service: CourseService = Depends(get_course_service),
    current_user: CurrentUser = Security(get_current_user, scopes=['courses:create']),
) -> CoursePublic:
    return await service.create_course(course_data, current_user.id)


@router.put(
    '/{course_id}',
    response_model=CoursePublic,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.bad_request_responses,
        **responses.common_responses,
    },
    dependencies=[Security(get_current_user, scopes=['courses:update'])]
)
@limiter.limit("10/minute")
async def update_course(
    request: Request,
    course_id: int,
    course_data: CourseUpdate,
    service: CourseService = Depends(get_course_service),
) -> CoursePublic:
    return await service.update_course(course_id, course_data)


@router.delete(
    '/{course_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.common_responses,
    },
    dependencies=[Security(get_current_user, scopes=['courses:delete'])]
)
@limiter.limit("10/minute")
async def delete_course(
    request: Request,
    course_id: int,
    service: CourseService = Depends(get_course_service),
) -> None:
    await service.delete_course(course_id)


@router.get(
    '/{course_id}/prerequisites',
    response_model=list[CoursePublic],
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.common_responses,
    },
    dependencies=[Security(get_current_user, scopes=['courses:read'])]
)
@limiter.limit("60/minute")
async def get_prerequisites(
    request: Request,
    course_id: int,
    service: CourseService = Depends(get_course_service),
) -> list[CoursePublic]:
    return await service.get_prerequisites(course_id)


@router.post(
    '/{course_id}/prerequisites',
    response_model=PrerequisitePublic,
    status_code=status.HTTP_201_CREATED,
    responses={
        **responses.auth_responses,
        **responses.bad_request_responses,
        **responses.common_responses,
    },
    dependencies=[Security(get_current_user, scopes=['courses:update'])]
)
@limiter.limit("10/minute")
async def add_prerequisite(
    request: Request,
    course_id: int,
    prerequisite_data: PrerequisiteCreate,
    service: CourseService = Depends(get_course_service),
) -> PrerequisitePublic:
    return await service.add_prerequisite(course_id, prerequisite_data)


@router.delete(
    '/{course_id}/prerequisites/{prerequisite_course_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.common_responses,
    },
    dependencies=[Security(get_current_user, scopes=['courses:update'])]
)
@limiter.limit("10/minute")
async def remove_prerequisite(
    request: Request,
    course_id: int,
    prerequisite_course_id: int,
    service: CourseService = Depends(get_course_service),
) -> None:
    await service.remove_prerequisite(course_id, prerequisite_course_id)
