from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.program import Program, ProgramCreate
from app.repositories.base import BaseRepository, ListResponse, FilterCondition
from app.core.constants import DEFAULT_SKIP, DEFAULT_LIMIT, FILTER_OPERATOR_CONTAINS
from app.schemas.filters import ProgramFilters


class ProgramRepository(BaseRepository[Program, ProgramCreate, ProgramCreate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Program, session)

    def _setup_filters(self):
        self.add_filter('title', operator=FILTER_OPERATOR_CONTAINS)
        self.add_filter('user_id')

    async def get_by_title(self, title: str) -> Optional[Program]:
        filters = self._create_filter_conditions_from_dict({'title': title})
        items, _ = await self.get_all(filters=filters, limit=DEFAULT_LIMIT)
        return items[0] if items else None

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

    async def get_by_id(self, program_id: int) -> Optional[Program]:
        query = select(Program).where(Program.id == program_id).options(selectinload(Program.user))
        result = await self.session.exec(query)
        return result.one_or_none()

    async def get_all(
            self,
            skip: int = DEFAULT_SKIP,
            limit: int = DEFAULT_LIMIT,
            filters: Optional[List[FilterCondition]] = None,
            order_by: Optional[str] = None,
            descending: bool = False,
    ) -> tuple[List[Program], int]:
        query = select(self.model).options(selectinload(Program.user))
        query = self._apply_filters(query, self.model, filters)
