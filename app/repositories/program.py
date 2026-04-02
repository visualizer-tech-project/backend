from typing import List, Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.program import Program, ProgramCreate, ProgramUpdate
from app.repositories.base import BaseRepository


class ProgramRepository(BaseRepository[Program, ProgramCreate, ProgramUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Program, session)

    async def get_by_title(self, title: str) -> Optional[Program]:
        """Получить программу по названию."""
        items, _ = await self.get_all(filters={'title': title}, limit=1)
        return items[0] if items else None

    async def get_by_user(
        self, user_id: int, skip: int = 0, limit: Optional[int] = None
    ) -> tuple[List[Program], int]:
        """Получить программы, созданные пользователем."""
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters={'user_id': user_id},
            order_by='created_at',
            descending=True,
        )

    async def get_by_ids(self, ids: List[int]) -> List[Program]:
        """Получить программы по списку ID."""
        if not ids:
            return []
        return await self.get_all(filters={'id': ids})
