from app.db.models import Review
from app.db.repositories.base import AsyncBaseRepository


class ReviewRepository(AsyncBaseRepository[Review]):
    def __init__(self) -> None:
        super().__init__(Review)
