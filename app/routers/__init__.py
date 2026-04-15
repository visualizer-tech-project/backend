from app.routers.careertrack import router as career_tracks_router
from app.routers.courses import router as courses_router
from app.routers.programs import router as programs_router
from app.routers.progress import router as progress_router
from app.routers.users import router as users_router
from app.routers.auth import router as auth_router
from app.routers.role import router as roles_router
from app.routers.permission import router as permissions_router

__all__ = [
    'users_router',
    'programs_router',
    'courses_router',
    'career_tracks_router',
    'progress_router',
    'auth_router',
    'roles_router',
    'permissions_router',
]
