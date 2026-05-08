from app.core import exceptions
from app.models.base import ListResponse
from app.models.course import Course, CourseCreate, CoursePublic, CourseUpdate
from app.models.prerequisite import Prerequisite, PrerequisitePublic, PrerequisiteCreate
from app.schemas.filters import CourseFilters
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
        result = await self._course_repo.get_filtered_paginated(filters)
        public_items = [CoursePublic.model_validate(item) for item in result.items]
        return ListResponse[CoursePublic](info=result.info, items=public_items)

    async def get_course_by_id(self, course_id: int) -> CoursePublic:
        course = await self._course_repo.get_by_id(course_id)
        if not course:
            raise exceptions.NotFoundError('Course not found')
        return CoursePublic.model_validate(course)

    async def create_course(
        self,
        course_data: CourseCreate,
        user_id: int,
    ) -> CoursePublic:
        program = await self._program_repo.get_by_id(course_data.program_id)
        if not program:
            raise exceptions.NotFoundError('Program not found')

        courses_in_program, _ = await self._course_repo.get_by_program(
            course_data.program_id
        )
        for existing_course in courses_in_program:
            if existing_course.title == course_data.title:
                raise exceptions.ConflictError(
                    'Course with this title already exists in program'
                )

        course = Course(
            title=course_data.title,
            description=course_data.description,
            type=course_data.type,
            program_id=course_data.program_id,
            user_id=user_id,
        )
        course = await self._course_repo.save(course)
        return CoursePublic.model_validate(course)

    async def update_course(
        self,
        course_id: int,
        course_data: CourseUpdate,
    ) -> CoursePublic:
        course = await self._course_repo.get_by_id(course_id)
        if not course:
            raise exceptions.NotFoundError('Course not found')

        if course_data.title:
            courses_in_program, _ = await self._course_repo.get_by_program(
                course.program_id
            )
            for existing_course in courses_in_program:
                if (
                    existing_course.title == course_data.title
                    and existing_course.id != course_id
                ):
                    raise exceptions.ConflictError(
                        'Course with this title already exists in program'
                    )

        update_dict = course_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(course, field, value)

        course = await self._course_repo.save(course)
        return CoursePublic.model_validate(course)

    async def delete_course(self, course_id: int) -> None:
        deleted = await self._course_repo.delete(course_id)
        if not deleted:
            raise exceptions.NotFoundError('Course not found')

    async def get_prerequisites(self, course_id: int) -> list[CoursePublic]:
        course = await self._course_repo.get_by_id(course_id)
        if not course:
            raise exceptions.NotFoundError('Course not found')

        prerequisites = await self._prerequisite_repo.get_by_course(course_id)

        items = []
        for prereq in prerequisites:
            prereq_course = await self._course_repo.get_by_id(
                prereq.prerequisite_course_id
            )
            if prereq_course:
                items.append(CoursePublic.model_validate(prereq_course))

        return items

    async def add_prerequisite(
        self,
        course_id: int,
        prerequisite_data: PrerequisiteCreate,
    ) -> PrerequisitePublic:
        course = await self._course_repo.get_by_id(course_id)
        if not course:
            raise exceptions.NotFoundError('Course not found')

        prereq_course_id = prerequisite_data.prerequisite_course_id
        prereq_course = await self._course_repo.get_by_id(prereq_course_id)
        if not prereq_course:
            raise exceptions.NotFoundError('Prerequisite course not found')

        if course_id == prereq_course_id:
            raise exceptions.BadRequestError('Cannot set self as prerequisite')

        existing = await self._prerequisite_repo.get_by_course_pair(
            course_id, prereq_course_id
        )
        if existing:
            raise exceptions.ConflictError('Prerequisite already exists')

        prerequisite = Prerequisite(
            course_id=course_id, prerequisite_course_id=prereq_course_id
        )
        prerequisite = await self._prerequisite_repo.save(prerequisite)
        return PrerequisitePublic.model_validate(prerequisite)

    async def remove_prerequisite(
        self, course_id: int, prerequisite_course_id: int
    ) -> None:
        removed = await self._prerequisite_repo.remove_prerequisite(
            course_id, prerequisite_course_id
        )
        if not removed:
            raise exceptions.NotFoundError('Prerequisite relation not found')
