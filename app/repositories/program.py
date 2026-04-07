from typing import List, Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.program import Program, ProgramCreate, ProgramUpdate
from app.repositories.base import BaseRepository, FilterCondition, ListResponse
from app.core.constants import DEFAULT_SKIP, DEFAULT_LIMIT
from app.schemas.filters import ProgramFilters


class ProgramRepository(BaseRepository[Program, ProgramCreate, ProgramCreate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Program, session)

    async def get_by_title(self, title: str) -> Optional[Program]:
        filters = [FilterCondition('title', title)]
        items, _ = await self.get_all(filters=filters, limit=DEFAULT_LIMIT)
        return items[0] if items else None

    async def get_by_user(
            self,
            user_id: int,
            skip: int = DEFAULT_SKIP,
            limit: int = DEFAULT_LIMIT
    ) -> tuple[List[Program], int]:
        filters = [FilterCondition('user_id', user_id)]
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
        filter_conditions = []

        if filters.title:
            filter_conditions.append(FilterCondition('title', filters.title, 'contains'))

        return await self.get_paginated(
            skip=filters.skip,
            limit=filters.limit,
            filters=filter_conditions if filter_conditions else None,
            order_by='created_at',
            descending=True,
        )
    