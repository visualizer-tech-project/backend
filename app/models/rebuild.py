"""Перестроение моделей для разрешения циклических ссылок"""


def rebuild_models():
    from app.models.user import User, UserPublic
    from app.models.program import Program, ProgramPublic
    from app.models.course import Course, CoursePublic
    from app.models.careertrack import (
        CareerTrack, CareerTrackPublic,
        CareerTrackWithCourses, CareerTrackCourse, CareerTrackCoursePublic
    )
    from app.models.userprogress import UserProgress, UserProgressPublic
    from app.models.prerequisite import Prerequisite, PrerequisitePublic
    from app.models.base import ListResponse

    User.model_rebuild()
    UserPublic.model_rebuild()

    Program.model_rebuild()
    ProgramPublic.model_rebuild()

    Course.model_rebuild()
    CoursePublic.model_rebuild()

    CareerTrack.model_rebuild()
    CareerTrackPublic.model_rebuild()
    CareerTrackWithCourses.model_rebuild()
    CareerTrackCourse.model_rebuild()
    CareerTrackCoursePublic.model_rebuild()

    UserProgress.model_rebuild()
    UserProgressPublic.model_rebuild()

    Prerequisite.model_rebuild()
    PrerequisitePublic.model_rebuild()

    ListResponse[ProgramPublic].model_rebuild()
    ListResponse[CoursePublic].model_rebuild()
    ListResponse[CareerTrackPublic].model_rebuild()
    ListResponse[UserPublic].model_rebuild()
    ListResponse[UserProgressPublic].model_rebuild()