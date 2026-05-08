from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from app.core.cors import setup_cors
from app.core.exception_handlers import register_exception_handlers
from app.core.middleware import add_middleware
from app.core.rate_limiter import setup_rate_limiter
from app.routers.auth import router as auth_router
from app.routers.careertrack import router as career_tracks_router
from app.routers.courses import router as courses_router
from app.routers.programs import router as programs_router
from app.routers.progress import router as progress_router
from app.routers.users import router as users_router
from app.routers.role import router as roles_router
from app.routers.permission import router as permissions_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title='EduMap API', version='1.0.0', lifespan=lifespan)

setup_cors(app)
setup_rate_limiter(app)
register_exception_handlers(app)
add_middleware(app)

api_v1_router = APIRouter(prefix='/api/v1')


@app.get('/health')
def health_check():
    return {'status': 'ok'}


api_v1_router.include_router(auth_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(programs_router)
api_v1_router.include_router(courses_router)
api_v1_router.include_router(career_tracks_router)
api_v1_router.include_router(progress_router)
api_v1_router.include_router(roles_router)
api_v1_router.include_router(permissions_router)

app.include_router(api_v1_router)
