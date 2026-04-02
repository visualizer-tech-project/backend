from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_course_service
from app.models.base import PaginatedResponse
from app.models.course import CourseCreate, CoursePublic, CourseUpdate
from app.models.filters import CourseFilters
from app.models.prerequisite import PrerequisiteCreate, PrerequisitePublic
from app.services.course import CourseService

router = APIRouter(prefix='/courses', tags=['courses'])


@router.get('/', response_model=PaginatedResponse[CoursePublic])
async def get_courses(
    filters: CourseFilters = Depends(),
    service: CourseService = Depends(get_course_service),
) -> PaginatedResponse[CoursePublic]:
    return await service.get_courses(filters)


@router.get('/{course_id}', response_model=CoursePublic)
async def get_course_by_id(
    course_id: int,
    service: CourseService = Depends(get_course_service),
) -> CoursePublic:
    try:
        return await service.get_course_by_id(course_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post('/', response_model=CoursePublic, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreate,
    service: CourseService = Depends(get_course_service),
) -> CoursePublic:
    try:
        return await service.create_course(course_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put('/{course_id}', response_model=CoursePublic)
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    service: CourseService = Depends(get_course_service),
) -> CoursePublic:
    try:
        return await service.update_course(course_id, course_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete('/{course_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int,
    service: CourseService = Depends(get_course_service),
) -> None:
    try:
        await service.delete_course(course_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get('/{course_id}/prerequisites', response_model=list[CoursePublic])
async def get_prerequisites(
    course_id: int,
    service: CourseService = Depends(get_course_service),
) -> list[CoursePublic]:
    try:
        return await service.get_prerequisites(course_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post('/{course_id}/prerequisites', response_model=PrerequisitePublic, status_code=status.HTTP_201_CREATED)
async def add_prerequisite(
    course_id: int,
    prerequisite_data: PrerequisiteCreate,
    service: CourseService = Depends(get_course_service),
) -> PrerequisitePublic:
    try:
        return await service.add_prerequisite(course_id, prerequisite_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete('/{course_id}/prerequisites/{prerequisite_course_id}', status_code=status.HTTP_204_NO_CONTENT)
async def remove_prerequisite(
    course_id: int,
    prerequisite_course_id: int,
    service: CourseService = Depends(get_course_service),
) -> None:
    try:
        await service.remove_prerequisite(course_id, prerequisite_course_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))