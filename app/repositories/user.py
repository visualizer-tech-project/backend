# app/repositories/user.py
from typing import List, Optional

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.course import Course
from app.models.user import User, UserRole
from app.models.userprogress import UserProgress
from app.repositories.base import BaseRepository
from app.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        query = select(User).where(User.email == email)
        result = await self.session.exec(query)
        return result.first()

    async def get_by_role(
        self,
        role: UserRole,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[User], int]:
        """Получить пользователей по роли"""
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters={'role': role},
            order_by='created_at',
            descending=True,
        )

    async def get_teachers(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[User], int]:
        """Получить всех преподавателей"""
        return await self.get_by_role(UserRole.TEACHER, skip, limit)

    async def get_students(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[User], int]:
        """Получить всех студентов"""
        return await self.get_by_role(UserRole.STUDENT, skip, limit)

    async def get_admins(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[User], int]:
        """Получить всех администраторов"""
        return await self.get_by_role(UserRole.ADMIN, skip, limit)

    async def update_role(self, user_id: int, role: UserRole) -> Optional[User]:
        """Обновить роль пользователя"""
        user = await self.get_by_id(user_id)
        if not user:
            return None

        user.role = role
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def assign_teacher_role(self, user_id: int) -> Optional[User]:
        """Назначить пользователю роль преподавателя"""
        return await self.update_role(user_id, UserRole.TEACHER)

    async def get_user_with_progress(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        program_id: Optional[int] = None,
    ) -> Optional[User]:
        """Получить пользователя с его прогрессом"""
        query = select(User).where(User.id == user_id)
        if status or program_id:
            progress_query = select(UserProgress).where(UserProgress.user_id == user_id)
            if status:
                progress_query = progress_query.where(UserProgress.status == status)
            if program_id:
                progress_query = progress_query.join(Course).where(
                    Course.program_id == program_id
                )
            progress_query = progress_query.offset(skip).limit(limit)
            progress_result = await self.session.exec(progress_query)
            progress_items = progress_result.all()
            user = await self.get_by_id(user_id)
            if user:
                user.progress = progress_items
            return user
        result = await self.session.exec(query)
        user = result.first()
        if user:
            await self.session.refresh(user, attribute_names=['progress'])
        return user

    async def search(
        self,
        query_str: str,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[User], int]:
        """Поиск пользователей по имени, фамилии или email"""
        search_pattern = f'%{query_str}%'

        base_query = select(User).where(
            (User.first_name.ilike(search_pattern))
            | (User.last_name.ilike(search_pattern))
            | (User.email.ilike(search_pattern))
        )
        count_query = select(func.count()).select_from(base_query.subquery())
        total = await self.session.scalar(count_query) or 0
        query = base_query.offset(skip).limit(limit)
        result = await self.session.exec(query)
        items = result.all()
        return items, total

    async def get_by_ids(self, ids: List[int]) -> List[User]:
        """Получить пользователей по списку ID"""
        if not ids:
            return []
        query = select(User).where(User.id.in_(ids))
        result = await self.session.exec(query)
        return result.all()

    async def count_by_role(self, role: Optional[UserRole] = None) -> int:
        """Подсчитать количество пользователей по роли"""
        query = select(func.count()).select_from(User)
        if role:
            query = query.where(User.role == role)
        return await self.session.scalar(query) or 0

    async def is_email_taken(
        self, email: str, exclude_user_id: Optional[int] = None
    ) -> bool:
        """
        Проверить, занят ли email.
        Args:
            email: Email для проверки
            exclude_user_id: ID пользователя, которого нужно исключить из проверки
        """
        query = select(User).where(User.email == email)
        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)
        result = await self.session.exec(query.limit(1))
        return result.first() is not None
