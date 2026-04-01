from datetime import datetime, timezone
from typing import List, Optional

from sqlmodel import and_, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.userprogress import UserProgress, UserProgressStatus
from app.repositories.base import BaseRepository
from app.schemas.userprogress import ProgressCreate, ProgressUpdate


class UserProgressRepository(
    BaseRepository[UserProgress, ProgressCreate, ProgressUpdate]
):
    def __init__(self, session: AsyncSession):
        super().__init__(UserProgress, session)

    async def get_by_user_and_course(
        self,
        user_id: int,
        course_id: int,
    ) -> Optional[UserProgress]:
        """Получить прогресс пользователя по курсу"""
        query = select(UserProgress).where(
            and_(UserProgress.user_id == user_id, UserProgress.course_id == course_id)
        )
        result = await self.session.exec(query)
        return result.first()

    async def get_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: Optional[int] = None,
        status: Optional[UserProgressStatus] = None,
        program_id: Optional[int] = None,
    ) -> tuple[List[UserProgress], int]:
        """Получить прогресс пользователя по всем курсам"""
        from app.models.course import Course

        base_query = select(UserProgress).where(UserProgress.user_id == user_id)

        if status:
            base_query = base_query.where(UserProgress.status == status)

        if program_id:
            base_query = base_query.join(Course).where(Course.program_id == program_id)

        count_query = select(func.count()).select_from(base_query.subquery())
        total = await self.session.scalar(count_query) or 0

        if limit is not None:
            query = base_query.offset(skip).limit(limit).order_by(UserProgress.updated_at.desc())
        else:
            query = base_query.offset(skip).order_by(UserProgress.updated_at.desc())

        result = await self.session.exec(query)
        return result.all(), total

    async def get_by_course(
        self,
        course_id: int,
        skip: int = 0,
        limit: Optional[int] = None,
        status: Optional[UserProgressStatus] = None,
    ) -> tuple[List[UserProgress], int]:
        """Получить прогресс всех пользователей по курсу"""
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

    async def create_or_update(
        self,
        progress_data: ProgressCreate,
    ) -> UserProgress:
        """Создать или обновить запись прогресса"""
        existing = await self.get_by_user_and_course(
            progress_data.user_id, progress_data.course_id
        )

        current_time = datetime.now(timezone.utc)

        if existing:
            update_dict = progress_data.model_dump(exclude_unset=True)
            update_dict.pop('user_id', None)
            update_dict.pop('course_id', None)

            if progress_data.status == UserProgressStatus.IN_PROGRESS:
                if not existing.started_at and 'started_at' not in update_dict:
                    update_dict['started_at'] = current_time

            elif progress_data.status == UserProgressStatus.COMPLETED:
                if not existing.completed_at and 'completed_at' not in update_dict:
                    update_dict['completed_at'] = current_time
                if not existing.started_at and 'started_at' not in update_dict:
                    update_dict['started_at'] = current_time

            for field, value in update_dict.items():
                setattr(existing, field, value)

            self.session.add(existing)
            await self.session.commit()
            await self.session.refresh(existing)
            return existing

        create_dict = progress_data.model_dump()

        if progress_data.status == UserProgressStatus.IN_PROGRESS:
            if not create_dict.get('started_at'):
                create_dict['started_at'] = current_time

        elif progress_data.status == UserProgressStatus.COMPLETED:
            if not create_dict.get('started_at'):
                create_dict['started_at'] = current_time
            if not create_dict.get('completed_at'):
                create_dict['completed_at'] = current_time

        new_progress = UserProgress(**create_dict)
        self.session.add(new_progress)
        await self.session.commit()
        await self.session.refresh(new_progress)
        return new_progress

    async def bulk_create(
        self,
        progress_data_list: List[ProgressCreate],
    ) -> List[UserProgress]:
        """Массовое создание записей прогресса"""
        results = []
        for progress_data in progress_data_list:
            progress = await self.create_or_update(progress_data)
            results.append(progress)
        return results