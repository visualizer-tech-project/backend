from typing import List, Optional

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.user import User, UserRole
from app.models.userprogress import UserProgress
from app.repositories.base import BaseRepository
from app.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        items, _ = await self.get_all(filters={'email': email}, limit=1)
        return items[0] if items else None

    async def get_by_role(
        self,
        role: UserRole,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> tuple[List[User], int]:
        """Получить пользователей по роли"""
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters={'role': role},
            order_by='created_at',
            descending=True,
        )

    async def get_by_ids(self, ids: List[int]) -> List[User]:
        """Получить пользователей по списку ID"""
        if not ids:
            return []
        query = select(User).where(User.id.in_(ids))
        result = await self.session.exec(query)
        return result.all()

    async def get_user_progress(
        self,
        user_id: int,
        skip: int = 0,
        limit: Optional[int] = None,
        status: Optional[str] = None,
        program_id: Optional[int] = None,
    ) -> tuple[List[UserProgress], int]:
        """Получить прогресс пользователя"""
        from app.models.course import Course

        base_query = select(UserProgress).where(UserProgress.user_id == user_id)

        if status:
            base_query = base_query.where(UserProgress.status == status)

        if program_id:
            base_query = base_query.join(Course).where(Course.program_id == program_id)

        count_query = select(func.count()).select_from(base_query.subquery())
        total = await self.session.scalar(count_query) or 0

        if limit is not None:
            query = base_query.offset(skip).limit(limit)
        else:
            query = base_query.offset(skip)

        result = await self.session.exec(query)
        return result.all(), total

    async def count_by_role(self, role: Optional[UserRole] = None) -> int:
        """Подсчитать количество пользователей по роли"""
        query = select(func.count()).select_from(User)
        if role:
            query = query.where(User.role == role)
        return await self.session.scalar(query) or 0

    async def is_email_taken(
        self, email: str, exclude_user_id: Optional[int] = None
    ) -> bool:
        """Проверить, занят ли email"""
        query = select(User).where(User.email == email)
        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)
        result = await self.session.exec(query.limit(1))
        return result.first() is not None