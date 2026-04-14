from fastapi import Depends

from app.dependencies.session import SessionDep
from app.repositories.careertrack import CareerTrackRepository
from app.repositories.course import CourseRepository
from app.repositories.prerequisite import PrerequisiteRepository
from app.repositories.program import ProgramRepository
from app.repositories.user import UserRepository
from app.repositories.userprogress import UserProgressRepository
from app.services.careertrack import CareerTrackService
from app.services.course import CourseService
from app.services.program import ProgramService
from app.services.progress import ProgressService
from app.services.user import UserService
from app.services.auth import AuthService
from app.repositories.refresh_session import RefreshSessionRepository



async def get_user_repo(session: SessionDep) -> UserRepository:
    return UserRepository(session)


async def get_program_repo(session: SessionDep) -> ProgramRepository:
    return ProgramRepository(session)


async def get_course_repo(session: SessionDep) -> CourseRepository:
    return CourseRepository(session)


async def get_prerequisite_repo(session: SessionDep) -> PrerequisiteRepository:
    return PrerequisiteRepository(session)


async def get_career_track_repo(session: SessionDep) -> CareerTrackRepository:
    return CareerTrackRepository(session)


async def get_user_progress_repo(session: SessionDep) -> UserProgressRepository:
    return UserProgressRepository(session)


async def get_user_service(
    user_repo: UserRepository = Depends(get_user_repo),
) -> UserService:
    return UserService(user_repo)


async def get_program_service(
    program_repo: ProgramRepository = Depends(get_program_repo),
    course_repo: CourseRepository = Depends(get_course_repo),
) -> ProgramService:
    return ProgramService(program_repo, course_repo)


async def get_course_service(
    course_repo: CourseRepository = Depends(get_course_repo),
    program_repo: ProgramRepository = Depends(get_program_repo),
    prerequisite_repo: PrerequisiteRepository = Depends(get_prerequisite_repo),
) -> CourseService:
    return CourseService(course_repo, program_repo, prerequisite_repo)


async def get_career_track_service(
    track_repo: CareerTrackRepository = Depends(get_career_track_repo),
    course_repo: CourseRepository = Depends(get_course_repo),
) -> CareerTrackService:
    return CareerTrackService(track_repo, course_repo)


async def get_progress_service(
    progress_repo: UserProgressRepository = Depends(get_user_progress_repo),
    course_repo: CourseRepository = Depends(get_course_repo),
    user_repo: UserRepository = Depends(get_user_repo),
) -> ProgressService:
    return ProgressService(progress_repo, course_repo, user_repo)

async def get_refresh_session_repo(session: SessionDep) -> RefreshSessionRepository:
    return RefreshSessionRepository(session)

async def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repo),
    refresh_session_repo: RefreshSessionRepository = Depends(get_refresh_session_repo),
) -> AuthService:
    return AuthService(user_repo, refresh_session_repo)
