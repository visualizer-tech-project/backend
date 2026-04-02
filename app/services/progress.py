from app.models.base import PageInfo, PaginatedResponse
from app.models.filters import ProgressFilters
from app.models.userprogress import (
    ProgressCreate,
    ProgressUpdate,
    UserProgressPublic,
    UserProgressWithDetails,
)
from app.repositories.course import CourseRepository
from app.repositories.user import UserRepository
from app.repositories.userprogress import UserProgressRepository


class ProgressService:
    def __init__(
        self,
        progress_repo: UserProgressRepository,
        course_repo: CourseRepository,
        user_repo: UserRepository,
    ) -> None:
        self._progress_repo = progress_repo
        self._course_repo = course_repo
        self._user_repo = user_repo

    async def get_user_progress(
        self,
        user_id: int,
        filters: ProgressFilters,
    ) -> PaginatedResponse[UserProgressWithDetails]:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise ValueError('User not found')

        progress_list, total = await self._progress_repo.get_by_user(
            user_id=user_id,
            skip=filters.skip,
            limit=filters.limit,
            status=filters.status,
            program_id=filters.program_id,
        )

        course_ids = [p.course_id for p in progress_list]
        courses = await self._course_repo.get_by_ids(course_ids) if course_ids else []
        courses_by_id = {c.id: c for c in courses}

        result_items = []
        for progress in progress_list:
            course = courses_by_id.get(progress.course_id)
            result_items.append(
                UserProgressWithDetails(
                    **UserProgressPublic.model_validate(progress).model_dump(),
                    course_title=course.title if course else None,
                    course_type=course.type.value if course else None,
                    program_id=course.program_id if course else None,
                    user_name=f"{user.first_name} {user.last_name}",
                    user_email=user.email,
                )
            )

        return PaginatedResponse(
            items=result_items,
            page_info=PageInfo(total=total, offset=filters.skip, limit=filters.limit),
        )

    async def create_progress(
        self,
        user_id: int,
        course_id: int,
        progress_data: ProgressCreate,
    ) -> UserProgressPublic:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise ValueError('User not found')

        course = await self._course_repo.get_by_id(course_id)
        if not course:
            raise ValueError('Course not found')

        existing = await self._progress_repo.get_by_user_and_course(user_id, course_id)
        if existing:
            raise ValueError('Progress record already exists')

        create_dict = progress_data.model_dump()
        create_dict['user_id'] = user_id
        create_dict['course_id'] = course_id

        progress = await self._progress_repo.create(create_dict)

        return UserProgressPublic.model_validate(progress)

    async def update_progress(
        self,
        user_id: int,
        course_id: int,
        progress_data: ProgressUpdate,
    ) -> UserProgressPublic:
        existing = await self._progress_repo.get_by_user_and_course(user_id, course_id)
        if not existing:
            raise ValueError('Progress record not found')

        updated_progress = await self._progress_repo.update(existing.id, progress_data)
        if not updated_progress:
            raise ValueError('Progress record not found')

        return UserProgressPublic.model_validate(updated_progress)

    async def delete_progress(self, user_id: int, course_id: int) -> None:
        progress = await self._progress_repo.get_by_user_and_course(user_id, course_id)
        if not progress:
            raise ValueError('Progress record not found')

        deleted = await self._progress_repo.delete(progress.id)
        if not deleted:
            raise ValueError('Progress record not found')