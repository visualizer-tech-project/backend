from typing import List, Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.program import Program, ProgramCreate
from app.repositories.base import BaseRepository, FilterCondition
from app.repositories.base import DEFAULT_SKIP, DEFAULT_LIMIT


class ProgramRepository(BaseRepository[Program, ProgramCreate, ProgramCreate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Program, session)

    async def get_by_title(self, title: str) -> Optional[Program]:
        """Получить программу по названию."""
        filters = [FilterCondition('title', title)]
        items, _ = await self.get_all(filters=filters, limit=1)
        return items[0] if items else None

    async def get_by_user(
        self, user_id: int, skip: int = DEFAULT_SKIP, limit: Optional[int] = DEFAULT_LIMIT
    ) -> tuple[List[Program], int]:
        """Получить программы, созданные пользователем."""
        filters = [FilterCondition('user_id', user_id)]
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by='created_at',
            descending=True,
        )