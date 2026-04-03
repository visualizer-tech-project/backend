from typing import List, Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.user import User, UserCreate, UserRole, UserUpdate
from app.repositories.base import BaseRepository, FilterCondition


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email."""
        filters = [FilterCondition('email', email)]
        items, _ = await self.get_all(filters=filters, limit=1)
        return items[0] if items else None

    async def get_by_role(
        self,
        role: UserRole,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> tuple[List[User], int]:
        """Получить пользователей по роли."""
        filters = [FilterCondition('role', role)]
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by='created_at',
            descending=True,
        )