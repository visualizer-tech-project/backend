from app.models.base import (
    BaseSQLModel,
    BaseSchema,
    BaseModelSchema,
    PaginationInfo,
    ListResponse,
)
from app.models.user import User, UserRole, UserCreate, UserUpdate, UserPublic
from app.models.program import Program, ProgramCreate, ProgramUpdate, ProgramPublic
from app.models.course import (
    Course,
    CourseType,
    CourseCreate,
    CourseUpdate,
    CoursePublic,
)
from app.models.prerequisite import Prerequisite, PrerequisiteCreate, PrerequisitePublic
from app.models.careertrack import (
    CareerTrack,
    CareerTrackCourse,
    CareerTrackCreate,
    CareerTrackUpdate,
    CareerTrackCoursePublic,
    CareerTrackPublic,
    CareerTrackWithCourses,
    TrackCourseItem,
)
from app.models.userprogress import (
    UserProgress,
    ProgressStatus,
    ProgressCreate,
    ProgressUpdate,
    UserProgressPublic,
)
from app.models.refresh_session import RefreshSession
from app.models.permission import (
    Permission,
    PermissionCreate,
    PermissionUpdate,
    PermissionPublic,
    RolePermissionMapping,
)
from app.models.role import Role, RoleCreate, RoleUpdate, RolePublic, UserRoleMapping
from app.models.email import EmailNotification, EmailAction

UserPublic.model_rebuild()
ProgramPublic.model_rebuild()
CoursePublic.model_rebuild()
PrerequisitePublic.model_rebuild()
CareerTrackPublic.model_rebuild()
TrackCourseItem.model_rebuild()
CareerTrackWithCourses.model_rebuild()
UserProgressPublic.model_rebuild()
PermissionPublic.model_rebuild()
RolePublic.model_rebuild()

ListResponse[ProgramPublic].model_rebuild()
ListResponse[CoursePublic].model_rebuild()
ListResponse[CareerTrackPublic].model_rebuild()
ListResponse[UserPublic].model_rebuild()
ListResponse[UserProgressPublic].model_rebuild()

__all__ = [
    'BaseSQLModel',
    'BaseSchema',
    'BaseModelSchema',
    'PaginationInfo',
    'ListResponse',
    'User',
    'UserRole',
    'UserCreate',
    'UserUpdate',
    'UserPublic',
    'Program',
    'ProgramCreate',
    'ProgramUpdate',
    'ProgramPublic',
    'Course',
    'CourseType',
    'CourseCreate',
    'CourseUpdate',
    'CoursePublic',
    'Prerequisite',
    'PrerequisiteCreate',
    'PrerequisitePublic',
    'CareerTrack',
    'CareerTrackCourse',
    'CareerTrackCreate',
    'CareerTrackUpdate',
    'CareerTrackCoursePublic',
    'CareerTrackPublic',
    'CareerTrackWithCourses',
    'TrackCourseItem',
    'UserProgress',
    'ProgressStatus',
    'ProgressCreate',
    'ProgressUpdate',
    'UserProgressPublic',
    'RefreshSession',
    'Permission',
    'PermissionCreate',
    'PermissionUpdate',
    'PermissionPublic',
    'RolePermissionMapping',
    'Role',
    'RoleCreate',
    'RoleUpdate',
    'RolePublic',
    'UserRoleMapping',
    'EmailNotification',
    'EmailAction',
]
