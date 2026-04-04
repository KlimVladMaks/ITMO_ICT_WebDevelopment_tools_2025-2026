from fastapi import FastAPI

from .database import init_db


async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
