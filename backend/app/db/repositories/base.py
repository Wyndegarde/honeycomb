from collections.abc import Sequence
from typing import Any

from sqlalchemy import ScalarResult, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase


class AsyncBaseRepository[T: DeclarativeBase]:
    """
    Base class for asynchronous repositories providing common CRUD operations.
    """

    def __init__(self, model: type[T]):
        self.model = model

    async def add(self, db: AsyncSession, obj: T) -> T:
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def create(self, db: AsyncSession, **kwargs: Any) -> T:
        obj = self.model(**kwargs)
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def get(self, db: AsyncSession, obj_id: Any) -> T | None:
        return await db.get(self.model, obj_id)  # type: ignore

    async def get_by_field(
        self, db: AsyncSession, field_name: str, value: Any
    ) -> T | None:
        if not hasattr(self.model, field_name):
            raise AttributeError(
                f"{self.model.__name__} has no field named '{field_name}'"
            )
        field = getattr(self.model, field_name)
        stmt = select(self.model).where(field == value)
        result = await db.execute(stmt)
        return result.scalars().first()  # type: ignore

    async def list_all(self, db: AsyncSession) -> Sequence[T]:
        stmt = select(self.model)
        result: ScalarResult[T] = await db.scalars(stmt)
        return result.all()  # type: ignore

    async def delete(self, db: AsyncSession, obj_id: Any) -> bool:
        obj = await db.get(self.model, obj_id)
        if not obj:
            return False
        await db.delete(obj)
        return True
