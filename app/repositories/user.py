from typing import List, Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.user import User, UserCreate, UserRole, UserUpdate
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email."""
        items, _ = await self.get_all(filters={'email': email}, limit=1)
        return items[0] if items else None

    async def get_by_role(
        self,
        role: UserRole,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> tuple[List[User], int]:
        """Получить пользователей по роли."""
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters={'role': role},
            order_by='created_at',
            descending=True,
        )

    async def get_by_ids(self, ids: List[int]) -> List[User]:
        """Получить пользователей по списку ID."""
        if not ids:
            return []
        query = select(User).where(User.id.in_(ids))
        result = await self.session.exec(query)
        return result.all()
