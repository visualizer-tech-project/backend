from typing import Annotated

from fastapi import APIRouter, Depends, Security, status

from app.core import responses
from app.core.security import get_current_user, CurrentUser
from app.dependencies import get_course_service
from app.models.base import ListResponse
from app.models.course import CourseCreate, CoursePublic, CourseUpdate
from app.models.prerequisite import PrerequisitePublic, PrerequisiteCreate
from app.schemas.filters import CourseFilters
from app.services.course import CourseService

router = APIRouter(prefix='/courses', tags=['courses'])


@router.get(
    '/',
    response_model=ListResponse[CoursePublic],
    responses={
        **responses.auth_responses,
        **responses.common_responses,
    }
)
async def get_courses(
    filters: CourseFilters = Depends(),
    service: CourseService = Depends(get_course_service),
    current_user: Annotated[
        CurrentUser,
        Security(get_current_user, scopes=['courses:list'])
    ] = None,
) -> ListResponse[CoursePublic]:
    if current_user is None:
        responses.raise_forbidden()
    return await service.get_courses(filters)


@router.get(
    '/{course_id}',
    response_model=CoursePublic,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.common_responses,
    }
)
async def get_course_by_id(
    course_id: int,
    service: CourseService = Depends(get_course_service),
    current_user: Annotated[
        CurrentUser,
        Security(get_current_user, scopes=['courses:read'])
    ] = None,
) -> CoursePublic:
    if current_user is None:
        responses.raise_forbidden()
    try:
        return await service.get_course_by_id(course_id)
    except ValueError as e:
        responses.raise_not_found(detail=str(e))


@router.post(
    '/',
    response_model=CoursePublic,
    status_code=status.HTTP_201_CREATED,
    responses={
        **responses.auth_responses,
        **responses.bad_request_responses,
        **responses.common_responses,
    }
)
async def create_course(
    course_data: CourseCreate,
    service: CourseService = Depends(get_course_service),
    current_user: Annotated[
        CurrentUser,
        Security(get_current_user, scopes=['courses:create'])
    ] = None,
) -> CoursePublic:
    if current_user is None:
        responses.raise_forbidden()
    try:
        return await service.create_course(course_data, current_user.id)
    except ValueError as e:
        responses.raise_bad_request(str(e))


@router.put(
    '/{course_id}',
    response_model=CoursePublic,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.bad_request_responses,
        **responses.common_responses,
    }
)
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    service: CourseService = Depends(get_course_service),
    current_user: Annotated[
        CurrentUser,
        Security(get_current_user, scopes=['courses:update'])
    ] = None,
) -> CoursePublic:
    if current_user is None:
        responses.raise_forbidden()
    try:
        return await service.update_course(course_id, course_data)
    except ValueError as e:
        if 'not found' in str(e):
            responses.raise_not_found(detail=str(e))
        responses.raise_bad_request(str(e))


@router.delete(
    '/{course_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.common_responses,
    }
)
async def delete_course(
    course_id: int,
    service: CourseService = Depends(get_course_service),
    current_user: Annotated[
        CurrentUser,
        Security(get_current_user, scopes=['courses:delete'])
    ] = None,
) -> None:
    if current_user is None:
        responses.raise_forbidden()
    try:
        await service.delete_course(course_id)
    except ValueError as e:
        responses.raise_not_found(detail=str(e))


@router.get(
    '/{course_id}/prerequisites',
    response_model=list[CoursePublic],
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.common_responses,
    }
)
async def get_prerequisites(
    course_id: int,
    service: CourseService = Depends(get_course_service),
    current_user: Annotated[
        CurrentUser,
        Security(get_current_user, scopes=['courses:read'])
    ] = None,
) -> list[CoursePublic]:
    if current_user is None:
        responses.raise_forbidden()
    try:
        return await service.get_prerequisites(course_id)
    except ValueError as e:
        responses.raise_not_found(detail=str(e))


@router.post(
    '/{course_id}/prerequisites',
    response_model=PrerequisitePublic,
    status_code=status.HTTP_201_CREATED,
    responses={
        **responses.auth_responses,
        **responses.bad_request_responses,
        **responses.common_responses,
    }
)
async def add_prerequisite(
    course_id: int,
    prerequisite_data: PrerequisiteCreate,
    service: CourseService = Depends(get_course_service),
    current_user: Annotated[
        CurrentUser,
        Security(get_current_user, scopes=['courses:update'])
    ] = None,
) -> PrerequisitePublic:
    if current_user is None:
        responses.raise_forbidden()
    try:
        return await service.add_prerequisite(course_id, prerequisite_data)
    except ValueError as e:
        responses.raise_bad_request(str(e))


@router.delete(
    '/{course_id}/prerequisites/{prerequisite_course_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        **responses.auth_responses,
        **responses.detail_responses,
        **responses.common_responses,
    }
)
async def remove_prerequisite(
    course_id: int,
    prerequisite_course_id: int,
    service: CourseService = Depends(get_course_service),
    current_user: Annotated[
        CurrentUser,
        Security(get_current_user, scopes=['courses:update'])
    ] = None,
) -> None:
    if current_user is None:
        responses.raise_forbidden()
    try:
        await service.remove_prerequisite(course_id, prerequisite_course_id)
    except ValueError as e:
        responses.raise_not_found(detail=str(e))