from app.dependencies.session import SessionDep
from app.dependencies.services import (
    get_user_repo,
    get_program_repo,
    get_course_repo,
    get_career_track_repo,
    get_user_progress_repo,
    get_auth_service,
    get_user_service,
    get_program_service,
    get_course_service,
    get_career_track_service,
    get_progress_service,
)
from app.dependencies.auth import (
    oauth2_scheme,
    get_current_user,
    get_current_active_user,
    require_admin,
    require_write_programs,
    require_delete_programs,
    require_write_courses,
    require_delete_courses,
    require_write_career_tracks,
    require_delete_career_tracks,
    require_read_users,
    require_write_users,
)

__all__ = [
    "SessionDep",

    "get_user_repo",
    "get_program_repo",
    "get_course_repo",
    "get_career_track_repo",
    "get_user_progress_repo",

    "get_auth_service",
    "get_user_service",
    "get_program_service",
    "get_course_service",
    "get_career_track_service",
    "get_progress_service",

    "oauth2_scheme",
    "get_current_user",
    "get_current_active_user",
    "require_admin",
    "require_write_programs",
    "require_delete_programs",
    "require_write_courses",
    "require_delete_courses",
    "require_write_career_tracks",
    "require_delete_career_tracks",
    "require_read_users",
    "require_write_users",
]