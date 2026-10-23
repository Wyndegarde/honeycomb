from collections.abc import Sequence
from typing import Any

from sqlalchemy import ScalarResult, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase


class AsyncBaseRepository[T: DeclarativeBase]:
    """
    Base class for asynchronous repositories providing common CRUD operations.
    """

    def __init__(self, model: type[T], db: AsyncSession):
        self.model = model
        self.db = db

    async def add(self, obj: T) -> T:
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def create(self, **kwargs: Any) -> T:
        return await self.add(self.model(**kwargs))

    async def get(self, obj_id: Any) -> T | None:
        return await self.db.get(self.model, obj_id)  # type: ignore

    async def get_by_field(self, field_name: str, value: Any) -> T | None:
        if not hasattr(self.model, field_name):
            raise AttributeError(
                f"{self.model.__name__} has no field named '{field_name}'"
            )
        field = getattr(self.model, field_name)
        stmt = select(self.model).where(field == value)
        result = await self.db.execute(stmt)
        return result.scalars().first()  # type: ignore

    async def list_all(self) -> Sequence[T]:
        stmt = select(self.model)
        result: ScalarResult[T] = await self.db.scalars(stmt)
        return result.all()  # type: ignore

    async def update(self, obj: T, **kwargs: Any) -> T:
        for key, value in kwargs.items():
            setattr(obj, key, value)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj_id: Any) -> bool:
        obj = await self.db.get(self.model, obj_id)
        if not obj:
            return False
        await self.db.delete(obj)
        return True
