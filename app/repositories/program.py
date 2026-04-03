from typing import List, Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.program import Program, ProgramCreate, ProgramUpdate
from app.repositories.base import BaseRepository, FilterCondition


class ProgramRepository(BaseRepository[Program, ProgramCreate, ProgramUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Program, session)

    async def get_by_title(self, title: str) -> Optional[Program]:
        """Получить программу по названию."""
        filters = [FilterCondition('title', title)]
        items, _ = await self.get_all(filters=filters, limit=1)
        return items[0] if items else None

    async def get_by_user(
        self, user_id: int, skip: int = 0, limit: Optional[int] = None
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