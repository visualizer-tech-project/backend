from typing import List

from app.models.base import BaseSchema
from app.models.course import CoursePublic


class CourseWithPrerequisites(BaseSchema):
    """Составная схема: курс с пререквизитами"""

    course: CoursePublic
    prerequisites: List[CoursePublic] = []
    prerequisite_for: List[CoursePublic] = []
