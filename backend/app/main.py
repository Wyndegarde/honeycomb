from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.db_engine import dispose_engine
from app.routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await dispose_engine()


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)
