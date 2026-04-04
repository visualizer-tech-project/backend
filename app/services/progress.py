from app.models.base import ListResponse, PaginationInfo
from app.schemas.filters import ProgressFilters
from app.models.userprogress import (
    ProgressCreate,
    ProgressUpdate,
    UserProgressPublic,
)
from app.schemas.userprogress import UserProgressWithDetails
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
    ) -> ListResponse[UserProgressWithDetails]:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise ValueError('User not found')

        progress_list, total = await self._progress_repo.get_by_user(
            user_id=user_id,
            skip=filters.skip,
            limit=filters.limit,
            status=filters.status,
        )

        course_ids = [p.course_id for p in progress_list]
        courses = await self._course_repo.get_by_ids(course_ids) if course_ids else []
        courses_by_id = {c.id: c for c in courses}

        page = (filters.skip // filters.limit) + 1 if filters.limit else 1
        pages_num = (total + filters.limit - 1) // filters.limit if filters.limit else 1

        items = []
        for progress in progress_list:
            course = courses_by_id.get(progress.course_id)
            items.append(
                UserProgressWithDetails(
                    progress=UserProgressPublic.model_validate(progress),
                    course=course,
                    user=user,
                )
            )

        return ListResponse(
            info=PaginationInfo(page=page, pages_num=pages_num, total=total),
            items=items,
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

        progress_data.user_id = user_id
        progress_data.course_id = course_id

        progress = await self._progress_repo.create_progress(progress_data)

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

        updated_progress = await self._progress_repo.update_progress(
            user_id, course_id, progress_data
        )
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
