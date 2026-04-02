from datetime import datetime, timezone
from typing import List, Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.userprogress import (
    ProgressCreate,
    ProgressStatus,
    ProgressUpdate,
    UserProgress,
)
from app.repositories.base import BaseRepository


class UserProgressRepository(
    BaseRepository[UserProgress, ProgressCreate, ProgressUpdate]
):
    def __init__(self, session: AsyncSession):
        super().__init__(UserProgress, session)

    async def get_by_user_and_course(
        self, user_id: int, course_id: int
    ) -> Optional[UserProgress]:
        """Получить прогресс пользователя по курсу."""
        items, _ = await self.get_all(
            filters={'user_id': user_id, 'course_id': course_id},
            limit=1,
        )
        return items[0] if items else None

    async def get_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: Optional[int] = 20,
        status: Optional[ProgressStatus] = None,
    ) -> tuple[List[UserProgress], int]:
        """Получить прогресс пользователя по всем курсам."""
        filters = {'user_id': user_id}
        if status:
            filters['status'] = status

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
        filters = {'course_id': course_id}
        if status:
            filters['status'] = status

        return await self.get_all(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by='updated_at',
            descending=True,
        )

    async def create_progress(self, progress_data: ProgressCreate) -> UserProgress:
        """Создать запись прогресса."""
        current_time = datetime.now(timezone.utc)
        create_dict = progress_data.model_dump()

        if progress_data.status == ProgressStatus.IN_PROGRESS:
            if not create_dict.get('started_at'):
                create_dict['started_at'] = current_time
        elif progress_data.status == ProgressStatus.COMPLETED:
            if not create_dict.get('started_at'):
                create_dict['started_at'] = current_time
            if not create_dict.get('completed_at'):
                create_dict['completed_at'] = current_time

        new_progress = UserProgress(**create_dict)
        return await self.save(new_progress)

    async def update_progress(
        self, user_id: int, course_id: int, progress_data: ProgressUpdate
    ) -> Optional[UserProgress]:
        """Обновить существующую запись прогресса."""
        existing = await self.get_by_user_and_course(user_id, course_id)
        if not existing:
            return None

        current_time = datetime.now(timezone.utc)
        update_dict = progress_data.model_dump(exclude_unset=True)

        if 'status' in update_dict:
            if update_dict['status'] == ProgressStatus.IN_PROGRESS:
                if not existing.started_at:
                    update_dict['started_at'] = current_time
            elif update_dict['status'] == ProgressStatus.COMPLETED:
                if not existing.started_at:
                    update_dict['started_at'] = current_time
                if not existing.completed_at:
                    update_dict['completed_at'] = current_time

        for field, value in update_dict.items():
            setattr(existing, field, value)

        return await self.save(existing)
