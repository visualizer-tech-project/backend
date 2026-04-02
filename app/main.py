from fastapi import APIRouter, FastAPI

from app.routers import (
    career_tracks_router,
    courses_router,
    programs_router,
    progress_router,
    users_router,
)

app = FastAPI(title='EduMap API', version='1.0.0')

api_v1_router = APIRouter(prefix='/api/v1')

api_v1_router.include_router(users_router)
api_v1_router.include_router(programs_router)
api_v1_router.include_router(courses_router)
api_v1_router.include_router(career_tracks_router)
api_v1_router.include_router(progress_router)

app.include_router(api_v1_router)


@app.get('/')
async def root() -> dict:
    return {'message': 'EduMap API', 'version': '1.0.0', 'docs': '/docs'}