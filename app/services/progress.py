from typing import Optional

from app.repositories.course import CourseRepository
from app.repositories.user import UserRepository
from app.repositories.userprogress import UserProgressRepository
from app.schemas.base import PageInfo, PaginatedResponse
from app.schemas.userprogress import (
    ProgressCreate,
    ProgressStatus,
    ProgressUpdate,
    UserProgressPublic,
    UserProgressWithDetails,
)


class ProgressService:
    """Сервис управления прогрессом студентов"""

    def __init__(
        self,
        progress_repo: UserProgressRepository,
        course_repo: CourseRepository,
        user_repo: UserRepository,
    ):
        self.progress_repo = progress_repo
        self.course_repo = course_repo
        self.user_repo = user_repo

    async def get_user_progress(
        self,
        user_id: int,
        status: Optional[ProgressStatus] = None,
        program_id: Optional[int] = None,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> PaginatedResponse[UserProgressWithDetails]:
        """Получить прогресс пользователя по курсам"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError('User not found')

        progress_list, total = await self.progress_repo.get_by_user(
            user_id=user_id,
            skip=skip,
            limit=limit,
            status=status,
            program_id=program_id,
        )

        result_items = []
        for progress in progress_list:
            course = await self.course_repo.get_by_id(progress.course_id)
            result_items.append(
                UserProgressWithDetails(
                    id=progress.id,
                    user_id=progress.user_id,
                    course_id=progress.course_id,
                    status=progress.status,
                    grade=progress.grade,
                    started_at=progress.started_at,
                    completed_at=progress.completed_at,
                    created_at=progress.created_at,
                    updated_at=progress.updated_at,
                    course_title=course.title if course else None,
                    course_type=course.type.value if course else None,
                    program_id=course.program_id if course else None,
                    user_name=f'{user.first_name} {user.last_name}',
                    user_email=user.email,
                )
            )

        return PaginatedResponse(
            items=result_items,
            page_info=PageInfo(total=total, offset=skip, limit=limit),
        )

    async def create_progress(
        self,
        user_id: int,
        course_id: int,
        progress_data: ProgressCreate,
    ) -> UserProgressPublic:
        """Отметить прогресс по курсу для пользователя"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError('User not found')

        course = await self.course_repo.get_by_id(course_id)
        if not course:
            raise ValueError('Course not found')

        existing = await self.progress_repo.get_by_user_and_course(user_id, course_id)
        if existing:
            raise ValueError('Progress record already exists')

        progress_data.user_id = user_id
        progress_data.course_id = course_id
        progress = await self.progress_repo.create_or_update(progress_data)

        return UserProgressPublic.model_validate(progress)

    async def update_progress(
        self,
        user_id: int,
        course_id: int,
        progress_data: ProgressUpdate,
    ) -> UserProgressPublic:
        """Обновить прогресс по курсу для пользователя"""
        existing = await self.progress_repo.get_by_user_and_course(user_id, course_id)
        if not existing:
            raise ValueError('Progress record not found')

        update_dict = progress_data.model_dump(exclude_unset=True)

        create_data = ProgressCreate(
            user_id=user_id,
            course_id=course_id,
            status=update_dict.get('status', existing.status),
            grade=update_dict.get('grade', existing.grade),
            started_at=update_dict.get('started_at', existing.started_at),
            completed_at=update_dict.get('completed_at', existing.completed_at),
        )

        progress = await self.progress_repo.create_or_update(create_data)

        return UserProgressPublic.model_validate(progress)

    async def delete_progress(
        self,
        user_id: int,
        course_id: int,
    ) -> None:
        """Удалить запись о прогрессе пользователя по курсу"""
        progress = await self.progress_repo.get_by_user_and_course(user_id, course_id)
        if not progress:
            raise ValueError('Progress record not found')

        deleted = await self.progress_repo.delete(progress.id)
        if not deleted:
            raise ValueError('Progress record not found')
