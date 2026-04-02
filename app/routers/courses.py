from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_course_service
from app.models.user import User
from app.schemas.base import PaginatedResponse
from app.schemas.course import CourseCreate, CoursePublic, CourseType, CourseUpdate
from app.schemas.prerequisite import PrerequisiteCreate, PrerequisitePublic
from app.services.course import CourseService

# Временная заглушка для текущего пользователя
DUMMY_USER = User(id=1, role='admin')

router = APIRouter(prefix='/courses', tags=['courses'])


@router.get(
    '/',
    response_model=PaginatedResponse[CoursePublic],
    summary='Получить список курсов',
)
async def get_courses(
    program_id: int = None,
    type: CourseType = None,
    title: str = None,
    skip: int = 0,
    limit: int = 20,
    course_service: CourseService = Depends(get_course_service),
) -> PaginatedResponse[CoursePublic]:
    """Получить список курсов с пагинацией и фильтрацией."""
    return await course_service.get_courses(program_id, type, title, skip, limit)


@router.get(
    '/{course_id}',
    response_model=CoursePublic,
    summary='Получить курс по ID',
)
async def get_course_by_id(
    course_id: int,
    course_service: CourseService = Depends(get_course_service),
) -> CoursePublic:
    """Получить информацию о курсе по ID."""
    try:
        return await course_service.get_course_by_id(course_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    '/',
    response_model=CoursePublic,
    status_code=status.HTTP_201_CREATED,
    summary='Создать новый курс',
)
async def create_course(
    course_data: CourseCreate,
    course_service: CourseService = Depends(get_course_service),
) -> CoursePublic:
    """Создать новый курс."""
    try:
        return await course_service.create_course(course_data, DUMMY_USER)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put(
    '/{course_id}',
    response_model=CoursePublic,
    summary='Обновить курс',
)
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    course_service: CourseService = Depends(get_course_service),
) -> CoursePublic:
    """Обновить курс."""
    try:
        return await course_service.update_course(course_id, course_data, DUMMY_USER)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    '/{course_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Удалить курс',
)
async def delete_course(
    course_id: int,
    course_service: CourseService = Depends(get_course_service),
) -> None:
    """Удалить курс."""
    try:
        await course_service.delete_course(course_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    '/{course_id}/prerequisites',
    response_model=list[CoursePublic],
    summary='Получить все пререквизиты для курса',
)
async def get_prerequisites(
    course_id: int,
    course_service: CourseService = Depends(get_course_service),
) -> list[CoursePublic]:
    """Получить список курсов-пререквизитов для указанного курса."""
    try:
        return await course_service.get_prerequisites(course_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    '/{course_id}/prerequisites',
    response_model=PrerequisitePublic,
    status_code=status.HTTP_201_CREATED,
    summary='Добавить пререквизит для курса',
)
async def add_prerequisite(
    course_id: int,
    prerequisite_data: PrerequisiteCreate,
    course_service: CourseService = Depends(get_course_service),
) -> PrerequisitePublic:
    """Добавить пререквизит для курса."""
    try:
        return await course_service.add_prerequisite(
            course_id, prerequisite_data, DUMMY_USER
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    '/{course_id}/prerequisites/{prerequisite_course_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Удалить пререквизит у курса',
)
async def remove_prerequisite(
    course_id: int,
    prerequisite_course_id: int,
    course_service: CourseService = Depends(get_course_service),
) -> None:
    """Удалить пререквизит у курса."""
    try:
        await course_service.remove_prerequisite(course_id, prerequisite_course_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
