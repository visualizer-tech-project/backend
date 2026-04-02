from typing import Optional

from app.models.user import User, UserRole
from app.repositories.user import UserRepository
from app.schemas.base import PageInfo, PaginatedResponse
from app.schemas.user import UserPublic, UserUpdate


class UserService:
    """Сервис управления пользователями"""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_users(
        self,
        role: Optional[UserRole] = None,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> PaginatedResponse[UserPublic]:
        """Получить список пользователей"""
        filters = {}
        if role:
            filters['role'] = role

        users, total = await self.user_repo.get_all(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by='created_at',
            descending=True,
        )

        return PaginatedResponse(
            items=[UserPublic.model_validate(user) for user in users],
            page_info=PageInfo(total=total, offset=skip, limit=limit),
        )

    async def get_user_by_id(self, user_id: int) -> UserPublic:
        """Получить пользователя по ID"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError('User not found')

        return UserPublic.model_validate(user)

    async def update_own_profile(
        self,
        user_id: int,
        user_data: UserUpdate,
    ) -> UserPublic:
        """Обновить свой профиль (только first_name, last_name)"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError('User not found')

        update_dict = user_data.model_dump(exclude_unset=True)
        allowed_fields = {'first_name', 'last_name'}
        filtered_dict = {k: v for k, v in update_dict.items() if k in allowed_fields}

        if not filtered_dict:
            return UserPublic.model_validate(user)

        updated_user = await self.user_repo.update(user_id, filtered_dict)
        if not updated_user:
            raise ValueError('User not found')

        return UserPublic.model_validate(updated_user)

    async def update_user_by_admin(
        self,
        user_id: int,
        user_data: UserUpdate,
    ) -> UserPublic:
        """Обновить пользователя (администратор)"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError('User not found')

        updated_user = await self.user_repo.update(user_id, user_data)
        if not updated_user:
            raise ValueError('User not found')

        return UserPublic.model_validate(updated_user)

    async def get_current_user(self, user_id: int) -> Optional[User]:
        """Получить текущего пользователя по ID"""
        return await self.user_repo.get_by_id(user_id)
