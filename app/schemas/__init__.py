from app.schemas.base import BaseModelSchema, BaseSchema, PageInfo, PaginatedResponse
from app.schemas.careertrack import (
    AddCourseToTrack,
    CareerTrackCoursePublic,
    CareerTrackCreate,
    CareerTrackPublic,
    CareerTrackUpdate,
    CareerTrackWithCourses,
    TrackCourseItem,
)
from app.schemas.course import (
    CourseCreate,
    CoursePublic,
    CourseType,
    CourseUpdate,
    CourseWithPrerequisites,
)
from app.schemas.prerequisite import (
    PrerequisiteCreate,
    PrerequisitePublic,
)
from app.schemas.program import (
    ProgramCopyRequest,
    ProgramCreate,
    ProgramPublic,
    ProgramUpdate,
)
from app.schemas.user import (
    LoginRequest,
    Token,
    UserCreate,
    UserDB,
    UserPublic,
    UserRole,
    UserUpdate,
)
from app.schemas.userprogress import (
    ProgressCreate,
    ProgressStatus,
    ProgressUpdate,
    UserProgressPublic,
    UserProgressWithDetails,
)

__all__ = [
    'BaseSchema',
    'BaseModelSchema',
    'PageInfo',
    'PaginatedResponse',
    'UserRole',
    'UserCreate',
    'UserUpdate',
    'LoginRequest',
    'UserPublic',
    'UserDB',
    'Token',
    'ProgramCreate',
    'ProgramUpdate',
    'ProgramPublic',
    'ProgramCopyRequest',
    'CourseType',
    'CourseCreate',
    'CourseUpdate',
    'CoursePublic',
    'CourseWithPrerequisites',
    'PrerequisiteCreate',
    'PrerequisitePublic',
    'CareerTrackCreate',
    'CareerTrackUpdate',
    'CareerTrackPublic',
    'CareerTrackCoursePublic',
    'CareerTrackWithCourses',
    'AddCourseToTrack',
    'TrackCourseItem',
    'ProgressStatus',
    'ProgressCreate',
    'ProgressUpdate',
    'UserProgressPublic',
    'UserProgressWithDetails',
]
