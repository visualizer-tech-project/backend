import math
from typing import Generic, List, Optional, Type, TypeVar, Any

from pydantic import BaseModel
from sqlalchemy import func
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.base import ListResponse, PaginationInfo
from app.core.constants import (
    DEFAULT_SKIP,
    DEFAULT_LIMIT,
    MAX_LIMIT,
    MIN_LIMIT,
    FILTER_OPERATOR_EQ,
    FILTER_OPERATOR_CONTAINS,
    FILTER_OPERATOR_STARTSWITH,
    FILTER_OPERATOR_IEXACT,
)

ModelType = TypeVar('ModelType', bound=SQLModel)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class FilterCondition:
    def __init__(self, field: str, value: Any, operator: str = FILTER_OPERATOR_EQ):
        self.field = field
        self.value = value
        self.operator = operator


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def save(self, db_obj: ModelType) -> ModelType:
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def get_by_id(self, item_id: int) -> Optional[ModelType]:
        return await self.session.get(self.model, item_id)

    def _apply_filters(self, query, model: Type[ModelType], filters: Optional[List[FilterCondition]] = None):
        if not filters:
            return query

        for filter_cond in filters:
            if not hasattr(model, filter_cond.field) or filter_cond.value is None:
                continue

            field = getattr(model, filter_cond.field)

            if filter_cond.operator == FILTER_OPERATOR_CONTAINS:
                query = query.where(field.contains(filter_cond.value))
            elif filter_cond.operator == FILTER_OPERATOR_STARTSWITH:
                query = query.where(field.startswith(filter_cond.value))
            elif filter_cond.operator == FILTER_OPERATOR_IEXACT:
                query = query.where(func.lower(field) == func.lower(filter_cond.value))
            else:
                query = query.where(field == filter_cond.value)

        return query

    async def get_all(
            self,
            skip: int = DEFAULT_SKIP,
            limit: int = DEFAULT_LIMIT,
            filters: Optional[List[FilterCondition]] = None,
            order_by: Optional[str] = None,
            descending: bool = False,
    ) -> tuple[List[ModelType], int]:
        query = select(self.model)
        query = self._apply_filters(query, self.model, filters)

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query) or 0

        if order_by and hasattr(self.model, order_by):
            order_field = getattr(self.model, order_by)
            if descending:
                query = query.order_by(order_field.desc())
            else:
                query = query.order_by(order_field)

        if limit > 0:
            query = query.limit(limit)
        query = query.offset(skip)

        result = await self.session.exec(query)
        items = result.all()
        return items, total

    async def get_paginated(
            self,
            skip: int = DEFAULT_SKIP,
            limit: int = DEFAULT_LIMIT,
            filters: Optional[List[FilterCondition]] = None,
            order_by: Optional[str] = None,
            descending: bool = False,
    ) -> ListResponse[ModelType]:
        if limit < MIN_LIMIT:
            limit = DEFAULT_LIMIT
        if limit > MAX_LIMIT:
            limit = MAX_LIMIT

        items, total = await self.get_all(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by=order_by,
            descending=descending,
        )

        page = (skip // limit) + 1 if limit > 0 else 1
        pages_num = (total + limit - 1) // limit if limit > 0 and total > 0 else 1

        pagination_info = PaginationInfo(
            total=total,
            page=page,
            pages_num=pages_num,
        )

        return ListResponse(info=pagination_info, items=items)

    async def create(self, create_data: CreateSchemaType) -> ModelType:
        db_obj = self.model(**create_data.model_dump())
        return await self.save(db_obj)

    async def update(
            self, item_id: int, update_data: UpdateSchemaType
    ) -> Optional[ModelType]:
        db_obj = await self.get_by_id(item_id)
        if not db_obj:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(db_obj, field, value)

        return await self.save(db_obj)

    async def delete(self, item_id: int) -> bool:
        db_obj = await self.get_by_id(item_id)
        if not db_obj:
            return False
        await self.session.delete(db_obj)
        await self.session.commit()
        return True

    async def exists(self, **kwargs) -> bool:
        query = select(self.model)
        for field, value in kwargs.items():
            if hasattr(self.model, field):
                query = query.where(getattr(self.model, field) == value)
        result = await self.session.exec(query.limit(1))
        return result.first() is not None

    async def get_all_for_model(
            self,
            model: Type[ModelType],
            skip: int = DEFAULT_SKIP,
            limit: int = DEFAULT_LIMIT,
            filters: Optional[List[FilterCondition]] = None,
            order_by: Optional[str] = None,
            descending: bool = False,
    ) -> tuple[List[ModelType], int]:
        query = select(model)
        query = self._apply_filters(query, model, filters)

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query) or 0

        if order_by and hasattr(model, order_by):
            order_field = getattr(model, order_by)
            if descending:
                query = query.order_by(order_field.desc())
            else:
                query = query.order_by(order_field)

        if limit > 0:
            query = query.limit(limit)
        query = query.offset(skip)

        result = await self.session.exec(query)
        return result.all(), total
