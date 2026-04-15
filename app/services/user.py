from app.models.base import ListResponse
from app.models.user import UserPublic, UserUpdate, UserRole
from app.schemas.filters import UserFilters
from app.repositories.user import UserRepository


class UserService:
    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    async def get_users(self, filters: UserFilters) -> ListResponse[UserPublic]:
        result = await self._user_repo.get_filtered_paginated(filters)
        result.items = [UserPublic.model_validate(item) for item in result.items]
        return result

    async def get_user_by_id(self, user_id: int) -> UserPublic:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise ValueError('User not found')
        return UserPublic.model_validate(user)

    async def get_user_by_email(self, email: str) -> UserPublic | None:
        user = await self._user_repo.get_by_email(email)
        if user:
            return UserPublic.model_validate(user)
        return None

    async def create_user(self, user_data) -> UserPublic:
        user = await self._user_repo.create(user_data)
        return UserPublic.model_validate(user)

    async def update_user(
        self,
        user_id: int,
        user_data: UserUpdate,
    ) -> UserPublic:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise ValueError('User not found')

        updated_user = await self._user_repo.update(user_id, user_data)
        if not updated_user:
            raise ValueError('User not found')

        return UserPublic.model_validate(updated_user)

    async def assign_teacher(self, user_id: int) -> UserPublic:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise ValueError('User not found')

        if user.role in (UserRole.TEACHER, UserRole.ADMIN):
            raise ValueError('User is already a teacher or admin')

        update_data = UserUpdate(role=UserRole.TEACHER)
        updated_user = await self._user_repo.update(user_id, update_data)
        if not updated_user:
            raise ValueError('User not found')

        return UserPublic.model_validate(updated_user)
