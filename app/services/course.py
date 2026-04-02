from typing import List, Optional

from app.models.user import User
from app.repositories.course import CourseRepository
from app.repositories.program import ProgramRepository
from app.schemas.base import PageInfo, PaginatedResponse
from app.schemas.course import (
    CourseCreate,
    CoursePublic,
    CourseType,
    CourseUpdate,
)
from app.schemas.prerequisite import PrerequisiteCreate, PrerequisitePublic


class CourseService:
    """Сервис управления курсами и пререквизитами"""

    def __init__(self, course_repo: CourseRepository, program_repo: ProgramRepository):
        self.course_repo = course_repo
        self.program_repo = program_repo

    async def get_courses(
        self,
        program_id: Optional[int] = None,
        course_type: Optional[CourseType] = None,
        title: Optional[str] = None,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> PaginatedResponse[CoursePublic]:
        """Получить список курсов"""
        filters = {}
        if program_id:
            filters['program_id'] = program_id
        if course_type:
            filters['type'] = course_type
        if title:
            filters['title'] = title

        courses, total = await self.course_repo.get_all(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by='created_at',
            descending=True,
        )

        return PaginatedResponse(
            items=[CoursePublic.model_validate(course) for course in courses],
            page_info=PageInfo(total=total, offset=skip, limit=limit),
        )

    async def get_course_by_id(self, course_id: int) -> CoursePublic:
        """Получить курс по ID"""
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise ValueError('Course not found')

        return CoursePublic.model_validate(course)

    async def create_course(
        self,
        course_data: CourseCreate,
        current_user: User,
    ) -> CoursePublic:
        """Создать новый курс"""
        program = await self.program_repo.get_by_id(course_data.program_id)
        if not program:
            raise ValueError('Program not found')

        if await self.course_repo.is_title_taken_in_program(
            course_data.title,
            course_data.program_id,
        ):
            raise ValueError('Course with this title already exists in program')

        course_dict = course_data.model_dump()
        course_dict['user_id'] = current_user.id

        course = await self.course_repo.create(course_dict)

        return CoursePublic.model_validate(course)

    async def update_course(
        self,
        course_id: int,
        course_data: CourseUpdate,
        current_user: User,
    ) -> CoursePublic:
        """Обновить курс"""
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise ValueError('Course not found')

        update_dict = course_data.model_dump(exclude_unset=True)
        if 'title' in update_dict:
            if await self.course_repo.is_title_taken_in_program(
                update_dict['title'],
                course.program_id,
                exclude_course_id=course_id,
            ):
                raise ValueError('Course with this title already exists in program')

        updated_course = await self.course_repo.update(course_id, course_data)
        if not updated_course:
            raise ValueError('Course not found')

        return CoursePublic.model_validate(updated_course)

    async def delete_course(self, course_id: int) -> None:
        """Удалить курс"""
        deleted = await self.course_repo.delete(course_id)
        if not deleted:
            raise ValueError('Course not found')

    async def get_prerequisites(
        self,
        course_id: int,
    ) -> List[CoursePublic]:
        """Получить все пререквизиты курса"""
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise ValueError('Course not found')

        prerequisites, _ = await self.course_repo.get_prerequisites_by_course(course_id)

        result = []
        for prereq in prerequisites:
            prereq_course = await self.course_repo.get_by_id(
                prereq.prerequisite_course_id
            )
            if prereq_course:
                result.append(CoursePublic.model_validate(prereq_course))

        return result

    async def add_prerequisite(
        self,
        course_id: int,
        prerequisite_data: PrerequisiteCreate,
        current_user: User,
    ) -> PrerequisitePublic:
        """Добавить пререквизит для курса"""
        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise ValueError('Course not found')

        prerequisite_course_id = prerequisite_data.prerequisite_course_id

        prerequisite_course = await self.course_repo.get_by_id(prerequisite_course_id)
        if not prerequisite_course:
            raise ValueError('Prerequisite course not found')

        if course_id == prerequisite_course_id:
            raise ValueError('Cannot set self as prerequisite')

        existing = await self.course_repo.get_prerequisite(
            course_id, prerequisite_course_id
        )
        if existing:
            raise ValueError('Prerequisite already exists')

        prerequisite = await self.course_repo.create_prerequisite(
            course_id, prerequisite_course_id
        )

        return PrerequisitePublic.model_validate(prerequisite)

    async def remove_prerequisite(
        self,
        course_id: int,
        prerequisite_course_id: int,
    ) -> None:
        """Удалить пререквизит у курса"""
        removed = await self.course_repo.delete_prerequisite(
            course_id, prerequisite_course_id
        )
        if not removed:
            raise ValueError('Prerequisite relation not found')