from datetime import datetime, timezone
from typing import Optional, List

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, update

from app.models.refresh_session import RefreshSession
from app.repositories.base import BaseRepository


class RefreshSessionRepository(BaseRepository[RefreshSession, None, None]):
    def __init__(self, session: AsyncSession):
        super().__init__(RefreshSession, session)

    async def get_by_jti(self, jti: str) -> Optional[RefreshSession]:
        filters = self._create_filter_conditions_from_dict({'jti': jti})
        items, _ = await self.get_all(filters=filters, limit=1)
        return items[0] if items else None

    async def get_valid_by_user_id(self, user_id: int) -> List[RefreshSession]:
        filters = self._create_filter_conditions_from_dict({
            'user_id': user_id,
            'is_valid': True,
        })
        items, _ = await self.get_all(filters=filters)
        valid_items = [
            item for item in items
            if item.expires_at > datetime.now(timezone.utc)
        ]
        return valid_items

    async def create_session(
            self,
            user_id: int,
            refresh_token_jti: str,
            expires_at: datetime,
    ) -> RefreshSession:
        session = RefreshSession(
            user_id=user_id,
            jti=refresh_token_jti,
            expires_at=expires_at,
            is_valid=True,
        )
        return await self.save(session)

    async def invalidate_session(self, jti: str) -> bool:
        session = await self.get_by_jti(jti)
        if not session:
            return False
        session.invalidate()
        await self.save(session)
        return True

    async def invalidate_all_user_sessions(self, user_id: int) -> int:
        active_sessions = await self.get_valid_by_user_id(user_id)
        count = len(active_sessions)

        await self.session.exec(
            update(RefreshSession)
            .where(RefreshSession.user_id == user_id)
            .where(RefreshSession.is_valid == True)
            .values(is_valid=False)
        )
        await self.session.commit()

        return count

    async def cleanup_expired_sessions(self) -> None:
        now = datetime.now(timezone.utc)
        query = select(RefreshSession).where(
            RefreshSession.expires_at < now
        )
        result = await self.session.exec(query)
        expired_sessions = result.all()

        for session in expired_sessions:
            await self.session.delete(session)

        await self.session.commit()
