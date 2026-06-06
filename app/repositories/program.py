from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.program import Program, ProgramCreate, ProgramUpdate
from app.models.user import User
from app.repositories.base import BaseRepository, ListResponse
from app.core.constants import DEFAULT_SKIP, DEFAULT_LIMIT, FILTER_OPERATOR_CONTAINS
from app.schemas.filters import ProgramFilters


class ProgramRepository(BaseRepository[Program, ProgramCreate, ProgramCreate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Program, session)

    def _setup_filters(self):
        self.add_filter('title', operator=FILTER_OPERATOR_CONTAINS)
        self.add_filter('user_id')

    async def get_by_id(self, item_id: int) -> Optional[Program]:
        query = (
            select(Program)
            .join(User, Program.user_id == User.id)
            .where(Program.id == item_id)
            .options(selectinload(Program.user))
        )
        result = await self.session.exec(query)
        return result.first()

    async def get_all(
        self,
        skip: int = DEFAULT_SKIP,
        limit: int = DEFAULT_LIMIT,
        filters=None,
        order_by: Optional[str] = None,
        descending: bool = False,
    ) -> tuple[List[Program], int]:
        query = select(Program).join(User, Program.user_id == User.id).options(
            selectinload(Program.user)
        )
        query = self._apply_filters(query, Program, filters)

        count_query = select(func.count()).select_from(Program).join(
            User, Program.user_id == User.id
        )
        count_query = self._apply_filters(count_query, Program, filters)
        total = await self.session.scalar(count_query) or 0

        if order_by and hasattr(Program, order_by):
            order_field = getattr(Program, order_by)
            query = query.order_by(order_field.desc() if descending else order_field)

        if limit > 0:
            query = query.limit(limit)
        query = query.offset(skip)

        result = await self.session.exec(query)
        return result.all(), total

    async def get_by_title(self, title: str) -> Optional[Program]:
        query = (
            select(Program)
            .where(Program.title == title)
            .limit(1)
        )
        result = await self.session.exec(query)
        return result.first()

    async def get_by_user(
        self, user_id: int, skip: int = DEFAULT_SKIP, limit: int = DEFAULT_LIMIT
    ) -> tuple[List[Program], int]:
        filters = self._create_filter_conditions_from_dict({'user_id': user_id})
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by='created_at',
            descending=True,
        )

    async def get_filtered_paginated(
        self,
        filters: ProgramFilters,
    ) -> ListResponse[Program]:
        filter_conditions = self._create_filter_conditions_from_model(filters)

        return await self.get_paginated(
            skip=filters.skip,
            limit=filters.limit,
            filters=filter_conditions if filter_conditions else None,
            order_by='created_at',
            descending=True,
        )
