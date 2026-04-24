from app.core import exceptions
from app.models.base import ListResponse
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
            raise exceptions.NotFoundError(f"User with id {user_id} not found")

        result = await self._progress_repo.get_filtered_paginated_by_user(
            user_id=user_id,
            filters=filters,
        )

        items = []
        for progress in result.items:
            course = await self._course_repo.get_by_id(progress.course_id)
            items.append(
                UserProgressWithDetails(
                    progress=UserProgressPublic.model_validate(progress),
                    course=course,
                    user=user,
                )
            )

        return ListResponse(
            info=result.info,
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
            raise exceptions.NotFoundError(f"User with id {user_id} not found")

        course = await self._course_repo.get_by_id(course_id)
        if not course:
            raise exceptions.NotFoundError(f"Course with id {course_id} not found")

        existing = await self._progress_repo.get_by_user_and_course(user_id, course_id)
        if existing:
            raise exceptions.ConflictError(f"Progress record already exists for user {user_id} and course {course_id}")

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
            raise exceptions.NotFoundError(f"Progress record not found for user {user_id} and course {course_id}")

        updated_progress = await self._progress_repo.update_progress(
            user_id, course_id, progress_data
        )
        if not updated_progress:
            raise exceptions.NotFoundError(f"Progress record not found for user {user_id} and course {course_id}")

        return UserProgressPublic.model_validate(updated_progress)

    async def delete_progress(self, user_id: int, course_id: int) -> None:
        progress = await self._progress_repo.get_by_user_and_course(user_id, course_id)
        if not progress:
            raise exceptions.NotFoundError(f"Progress record not found for user {user_id} and course {course_id}")

        deleted = await self._progress_repo.delete(progress.id)
        if not deleted:
            raise exceptions.NotFoundError(f"Progress record not found for user {user_id} and course {course_id}")
