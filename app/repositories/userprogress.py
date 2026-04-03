from typing import List, Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.userprogress import (
    ProgressCreate,
    ProgressStatus,
    ProgressUpdate,
    UserProgress,
)
from app.repositories.base import BaseRepository, FilterCondition


class UserProgressRepository(
    BaseRepository[UserProgress, ProgressCreate, ProgressUpdate]
):
    def __init__(self, session: AsyncSession):
        super().__init__(UserProgress, session)

    async def get_by_user_and_course(
            self, user_id: int, course_id: int
    ) -> Optional[UserProgress]:
        """Получить прогресс пользователя по курсу."""
        filters = [
            FilterCondition('user_id', user_id),
            FilterCondition('course_id', course_id),
        ]
        items, _ = await self.get_all(filters=filters, limit=1)
        return items[0] if items else None

    async def get_by_user(
            self,
            user_id: int,
            skip: int = 0,
            limit: Optional[int] = None,
            status: Optional[ProgressStatus] = None,
    ) -> tuple[List[UserProgress], int]:
        """Получить прогресс пользователя по всем курсам."""
        filters = [FilterCondition('user_id', user_id)]
        if status:
            filters.append(FilterCondition('status', status))

        return await self.get_all(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by='updated_at',
            descending=True,
        )

    async def get_by_course(
            self,
            course_id: int,
            skip: int = 0,
            limit: Optional[int] = 20,
            status: Optional[ProgressStatus] = None,
    ) -> tuple[List[UserProgress], int]:
        """Получить прогресс всех пользователей по курсу."""
        filters = [FilterCondition('course_id', course_id)]
        if status:
            filters.append(FilterCondition('status', status))

        return await self.get_all(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by='updated_at',
            descending=True,
        )

    async def create_progress(self, progress_data: ProgressCreate) -> UserProgress:
        """Создать запись прогресса."""
        progress = UserProgress.create_with_defaults(
            user_id=progress_data.user_id,
            course_id=progress_data.course_id,
            status=progress_data.status,
            grade=progress_data.grade,
            started_at=progress_data.started_at,
            completed_at=progress_data.completed_at,
        )
        return await self.save(progress)

    async def update_progress(
            self, user_id: int, course_id: int, progress_data: ProgressUpdate
    ) -> Optional[UserProgress]:
        """Обновить существующую запись прогресса."""
        existing = await self.get_by_user_and_course(user_id, course_id)
        if not existing:
            return None

        update_dict = progress_data.model_dump(exclude_unset=True)
        existing.__dict__.update(update_dict)

        if 'status' in update_dict:
            existing.update_status_with_dates(update_dict['status'])

        return await self.save(existing)