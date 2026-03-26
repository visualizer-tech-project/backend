from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel
from sqlmodel import SQLModel, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

ModelType = TypeVar('ModelType', bound=SQLModel)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Получить запись по ID."""
        return await self.session.get(self.model, id)

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        descending: bool = False,
    ) -> tuple[List[ModelType], int]:
        """
        Получить список записей с пагинацией и фильтрацией.
        Args:
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей
            filters: Словарь фильтров {field_name: value}
            order_by: Поле для сортировки
            descending: Направление сортировки (True - по убыванию)
        Returns:
            Кортеж (список записей, общее количество)
        """
        query = select(self.model)
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.where(getattr(self.model, field) == value)
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query) or 0
        if order_by and hasattr(self.model, order_by):
            order_field = getattr(self.model, order_by)
            if descending:
                query = query.order_by(order_field.desc())
            else:
                query = query.order_by(order_field)
        query = query.offset(skip).limit(limit)
        result = await self.session.exec(query)
        items = result.all()
        return items, total

    async def create(self, create_data: CreateSchemaType) -> ModelType:
        """Создать новую запись."""
        db_obj = self.model(**create_data.model_dump())
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(
        self, id: int, update_data: UpdateSchemaType
    ) -> Optional[ModelType]:
        """Обновить существующую запись."""
        db_obj = await self.get_by_id(id)
        if not db_obj:
            return None
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(db_obj, field, value)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, id: int) -> bool:
        """Удалить запись по ID."""
        db_obj = await self.get_by_id(id)
        if not db_obj:
            return False
        await self.session.delete(db_obj)
        await self.session.commit()
        return True

    async def exists(self, **kwargs) -> bool:
        """Проверить существование записи по условиям."""
        query = select(self.model)
        for field, value in kwargs.items():
            if hasattr(self.model, field):
                query = query.where(getattr(self.model, field) == value)
        result = await self.session.exec(query.limit(1))
        return result.first() is not None
