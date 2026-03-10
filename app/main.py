from contextlib import asynccontextmanager

from fastapi import FastAPI

from .core.database import create_db_and_tables

app = FastAPI()


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    yield


@app.get('/')
def main_page():
    return {'Hello': 'World'}


@app.get('/items/{item_id}')
def get_item(item_id: int):
    return {'item_id': item_id}
