from fastapi import FastAPI

from app.routers import (
    auth_router,
    career_tracks_router,
    courses_router,
    programs_router,
    progress_router,
    users_router,
)

app = FastAPI(title='EduMap API', version='1.0.0')

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(programs_router)
app.include_router(courses_router)
app.include_router(career_tracks_router)
app.include_router(progress_router)
