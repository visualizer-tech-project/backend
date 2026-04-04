from typing import List, Optional

from app.dependencies.current_user import get_current_user_id
from app.models.base import ListResponse
from app.models.course import CourseCreate, CoursePublic, CourseUpdate
from app.models.prerequisite import PrerequisitePublic, PrerequisiteCreate
from app.schemas.filters import CourseFilters
from app.repositories.base import FilterCondition
from app.repositories.course import CourseRepository
from app.repositories.program import ProgramRepository
from app.repositories.prerequisite import PrerequisiteRepository


class CourseService:
    def __init__(
        self,
        course_repo: CourseRepository,
        program_repo: ProgramRepository,
        prerequisite_repo: PrerequisiteRepository,
    ) -> None:
        self._course_repo = course_repo
        self._program_repo = program_repo
        self._prerequisite_repo = prerequisite_repo

    async def get_courses(
        self,
        filters: CourseFilters,
    ) -> ListResponse[CoursePublic]:
        filter_conditions = []
        if filters.program_id:
            filter_conditions.append(FilterCondition('program_id', filters.program_id))
        if filters.type:
            filter_conditions.append(FilterCondition('type', filters.type))
        if filters.title:
            filter_conditions.append(FilterCondition('title', filters.title))

        page = (filters.skip // filters.limit) + 1 if filters.limit else 1

        result = await self._course_repo.get_paginated(
            page=page,
            limit=filters.limit,
            filters=filter_conditions if filter_conditions else None,
            order_by='created_at',
            descending=True,
        )

        result.items = [CoursePublic.model_validate(item) for item in result.items]
        return result

    async def get_course_by_id(self, course_id: int) -> CoursePublic:
        course = await self._course_repo.get_by_id(course_id)
        if not course:
            raise ValueError('Course not found')
        return CoursePublic.model_validate(course)

    async def create_course(self, course_data: CourseCreate) -> CoursePublic:
        program = await self._program_repo.get_by_id(course_data.program_id)
        if not program:
            raise ValueError('Program not found')

        courses_in_program, _ = await self._course_repo.get_by_program(course_data.program_id)
        for existing_course in courses_in_program:
            if existing_course.title == course_data.title:
                raise ValueError('Course with this title already exists in program')

        user_id = await get_current_user_id()
        course_dict = course_data.model_dump()
        course_dict['user_id'] = user_id

        course = await self._course_repo.create(course_dict)
        return CoursePublic.model_validate(course)

    async def update_course(
        self,
        course_id: int,
        course_data: CourseUpdate,
    ) -> CoursePublic:
        course = await self._course_repo.get_by_id(course_id)
        if not course:
            raise ValueError('Course not found')

        if course_data.title:
            courses_in_program, _ = await self._course_repo.get_by_program(course.program_id)
            for existing_course in courses_in_program:
                if existing_course.title == course_data.title and existing_course.id != course_id:
                    raise ValueError('Course with this title already exists in program')

        updated_course = await self._course_repo.update(course_id, course_data)
        if not updated_course:
            raise ValueError('Course not found')

        return CoursePublic.model_validate(updated_course)

    async def delete_course(self, course_id: int) -> None:
        deleted = await self._course_repo.delete(course_id)
        if not deleted:
            raise ValueError('Course not found')

    async def get_prerequisites(self, course_id: int) -> List[CoursePublic]:
        course = await self._course_repo.get_by_id(course_id)
        if not course:
            raise ValueError('Course not found')

        prerequisites = await self._prerequisite_repo.get_by_course(course_id)

        if not prerequisites:
            return []

        prerequisite_ids = [p.prerequisite_course_id for p in prerequisites]
        prerequisite_courses = await self._course_repo.get_by_ids(prerequisite_ids)

        return [CoursePublic.model_validate(c) for c in prerequisite_courses]

    async def add_prerequisite(
        self,
        course_id: int,
        prerequisite_data: PrerequisiteCreate,
    ) -> PrerequisitePublic:
        course = await self._course_repo.get_by_id(course_id)
        if not course:
            raise ValueError('Course not found')

        prereq_course_id = prerequisite_data.prerequisite_course_id
        prereq_course = await self._course_repo.get_by_id(prereq_course_id)
        if not prereq_course:
            raise ValueError('Prerequisite course not found')

        if course_id == prereq_course_id:
            raise ValueError('Cannot set self as prerequisite')

        existing = await self._prerequisite_repo.get_by_course_pair(course_id, prereq_course_id)
        if existing:
            raise ValueError('Prerequisite already exists')

        prerequisite = await self._prerequisite_repo.add_prerequisite(course_id, prereq_course_id)

        return PrerequisitePublic.model_validate(prerequisite)

    async def remove_prerequisite(self, course_id: int, prerequisite_course_id: int) -> None:
        removed = await self._prerequisite_repo.remove_prerequisite(course_id, prerequisite_course_id)
        if not removed:
            raise ValueError('Prerequisite relation not found')