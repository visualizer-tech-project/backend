from typing import List, Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.user import User, UserCreate, UserRole, UserUpdate
from app.repositories.base import BaseRepository, FilterCondition, ListResponse
from app.core.constants import DEFAULT_SKIP, DEFAULT_LIMIT
from app.schemas.filters import UserFilters


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        filters = [FilterCondition('email', email)]
        items, _ = await self.get_all(filters=filters, limit=DEFAULT_LIMIT)
        return items[0] if items else None

    async def get_by_role(
            self,
            role: UserRole,
            skip: int = DEFAULT_SKIP,
            limit: int = DEFAULT_LIMIT,
    ) -> tuple[List[User], int]:
        filters = [FilterCondition('role', role)]
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by='created_at',
            descending=True,
        )

    async def get_filtered_paginated(
            self,
            filters: UserFilters,
    ) -> ListResponse[User]:
        filter_conditions = []

        if filters.role:
            filter_conditions.append(FilterCondition('role', filters.role))

        return await self.get_paginated(
            skip=filters.skip,
            limit=filters.limit,
            filters=filter_conditions if filter_conditions else None,
            order_by='created_at',
            descending=True,
        )
