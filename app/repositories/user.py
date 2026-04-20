from typing import List, Optional, Sequence
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.user import User, UserCreate, UserRole, UserUpdate
from app.models.role import Role
from app.repositories.base import BaseRepository, ListResponse
from app.core.constants import DEFAULT_SKIP, DEFAULT_LIMIT
from app.schemas.filters import UserFilters


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    def _setup_filters(self):
        self.add_filter('email')
        self.add_filter('role')

    async def get_by_email(self, email: str) -> Optional[User]:
        filters = self._create_filter_conditions_from_dict({'email': email})
        items, _ = await self.get_all(filters=filters, limit=DEFAULT_LIMIT)
        return items[0] if items else None

    async def get_by_role(
            self,
            role: UserRole,
            skip: int = DEFAULT_SKIP,
            limit: int = DEFAULT_LIMIT,
    ) -> tuple[List[User], int]:
        filters = self._create_filter_conditions_from_dict({'role': role})
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
        filter_conditions = self._create_filter_conditions_from_model(filters)
        return await self.get_paginated(
            skip=filters.skip,
            limit=filters.limit,
            filters=filter_conditions if filter_conditions else None,
            order_by='created_at',
            descending=True,
        )

    async def get_with_roles(self, user_id: int) -> Optional[User]:
        user = await self.get_by_id(user_id)
        if user:
            await self.session.refresh(user, ['roles'])
        return user

    async def get_user_roles(self, user_id: int) -> Sequence[Role]:
        user = await self.get_with_roles(user_id)
        return user.roles if user else []

    async def set_user_roles(self, user_id: int, role_ids: List[int]) -> Optional[User]:

        user = await self.session.get(User, user_id)
        if not user:
            return None

        if role_ids:
            roles = await self.session.exec(
                select(Role).where(Role.id.in_(role_ids))
            )
            user.roles = list(roles.all())
        else:
            user.roles = []

        await self.session.commit()
        await self.session.refresh(user, ['roles'])
        return user