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
        limit: int = 20,
    ) -> PaginatedResponse[UserPublic]:
        """Получить список пользователей"""
        if role:
            users, total = await self.user_repo.get_by_role(role, skip, limit)
        else:
            users, total = await self.user_repo.get_all(
                skip=skip,
                limit=limit,
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

    async def update_user(
        self,
        user_id: int,
        user_data: UserUpdate,
        current_user: User,
    ) -> UserPublic:
        """Обновить данные пользователя"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError('User not found')

        if current_user.id != user_id and current_user.role != UserRole.ADMIN:
            raise ValueError('Cannot edit this user')

        update_dict = user_data.model_dump(exclude_unset=True)
        if 'email' in update_dict:
            if await self.user_repo.is_email_taken(
                update_dict['email'], exclude_user_id=user_id
            ):
                raise ValueError('Email already taken')

        updated_user = await self.user_repo.update(user_id, user_data)
        if not updated_user:
            raise ValueError('User not found')

        return UserPublic.model_validate(updated_user)

    async def assign_teacher_role(
        self,
        user_id: int,
        current_user: User,
    ) -> UserPublic:
        """Назначить пользователю роль преподавателя"""
        if current_user.role != UserRole.ADMIN:
            raise PermissionError('Admin privileges required')

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError('User not found')

        if user.role in [UserRole.TEACHER, UserRole.ADMIN]:
            raise ValueError('User is already a teacher or admin')

        updated_user = await self.user_repo.assign_teacher_role(user_id)
        if not updated_user:
            raise ValueError('User not found')

        return UserPublic.model_validate(updated_user)

    async def get_current_user(self, user_id: int) -> Optional[User]:
        """Получить текущего пользователя по ID (для зависимостей)"""
        return await self.user_repo.get_by_id(user_id)
