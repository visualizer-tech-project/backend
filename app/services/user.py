from app.dependencies.current_user import get_current_user_id
from app.models.base import PageInfo, PaginatedResponse
from app.models.filters import UserFilters
from app.models.user import UserPublic, UserUpdate, UserRole
from app.repositories.user import UserRepository


class UserService:
    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    async def get_users(self, filters: UserFilters) -> PaginatedResponse[UserPublic]:
        filter_dict = filters.model_dump(exclude={'skip', 'limit'}, exclude_none=True)

        users, total = await self._user_repo.get_all(
            skip=filters.skip,
            limit=filters.limit,
            filters=filter_dict if filter_dict else None,
            order_by='created_at',
            descending=True,
        )

        return PaginatedResponse(
            items=[UserPublic.model_validate(user) for user in users],
            page_info=PageInfo(total=total, offset=filters.skip, limit=filters.limit),
        )

    async def get_user_by_id(self, user_id: int) -> UserPublic:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise ValueError('User not found')
        return UserPublic.model_validate(user)

    async def update_own_profile(self, user_data: UserUpdate) -> UserPublic:
        user_id = await get_current_user_id()
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise ValueError('User not found')

        updated_user = await self._user_repo.update(user_id, user_data)
        if not updated_user:
            raise ValueError('User not found')

        return UserPublic.model_validate(updated_user)

    async def update_user_by_admin(
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
        """Назначить пользователю роль преподавателя."""
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