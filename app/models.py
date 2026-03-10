from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import DateTime, Numeric, Text
from sqlalchemy.sql import func
from sqlmodel import Column, Field, Relationship, SQLModel


class UserRole(str, Enum):
    ADMIN = 'admin'
    USER = 'user'
    TEACHER = 'teacher'


class UserProgressStatus(str, Enum):
    NOT_STARTED = 'not_started'
    IN_PROCESS = 'in_process'
    FINISHED = 'finished'


class User(SQLModel, table=True):
    __tablename__ = 'users'

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, max_length=255, index=True)
    hashed_password: str
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    role: UserRole
    created_at: Optional[datetime] = Field(
        column=Column(DateTime, server_default=func.now())
    )

    programs: List['Program'] = Relationship(back_populates='user')
    courses: List['Course'] = Relationship(back_populates='user')
    progress: List['UserProgress'] = Relationship(back_populates='user')
    career_tracks: List['CareerTrack'] = Relationship(back_populates='user')


class Program(SQLModel, table=True):
    __tablename__ = 'programs'

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(unique=True, max_length=255, index=True)
    description: str = Field(sa_column=Column(Text))
    user_id: int = Field(foreign_key='users.id')
    created_at: Optional[datetime] = Field(
        column=Column(DateTime, server_default=func.now())
    )

    user: User = Relationship(back_populates='programs')
    courses: List['Course'] = Relationship(back_populates='program')


class Course(SQLModel, table=True):
    __tablename__ = 'courses'

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(unique=True, max_length=255, index=True)
    description: str = Field(sa_column=Column(Text))
    program_id: int = Field(foreign_key='programs.id')
    user_id: int = Field(foreign_key='users.id')
    created_at: Optional[datetime] = Field(
        column=Column(DateTime, server_default=func.now())
    )

    program: Program = Relationship(back_populates='courses')
    user: User = Relationship(back_populates='courses')
    prerequisites: List['Prerequisite'] = Relationship(back_populates='course')
    progress: List['UserProgress'] = Relationship(back_populates='course')
    career_track_courses: List['CareerTrackCourse'] = Relationship(
        back_populates='course'
    )


class Prerequisite(SQLModel, table=True):
    __tablename__ = 'prerequisites'

    id: Optional[int] = Field(default=None, primary_key=True)
    course_id: int = Field(foreign_key='courses.id')
    prerequisite_course_id: int = Field(foreign_key='courses.id')
    created_at: Optional[datetime] = Field(
        column=Column(DateTime, server_default=func.now())
    )

    course: Course = Relationship(
        back_populates='prerequisites', foreign_keys='Prerequisite.course_id'
    )
    prerequisite_course: Course = Relationship(
        foreign_keys='Prerequisite.prerequisite_course_id'
    )


class UserProgress(SQLModel, table=True):
    __tablename__ = 'user_progress'

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key='users.id')
    course_id: int = Field(foreign_key='courses.id')
    progress: UserProgressStatus
    grade: Optional[float] = Field(default=None, sa_column=Column(Numeric(5, 2)))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = Field(
        column=Column(DateTime, server_default=func.now())
    )

    user: User = Relationship(back_populates='progress')
    course: Course = Relationship(back_populates='progress')


class CareerTrack(SQLModel, table=True):
    __tablename__ = 'career_tracks'

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(unique=True, max_length=255, index=True)
    description: str = Field(sa_column=Column(Text))
    user_id: int = Field(foreign_key='users.id')
    created_at: Optional[datetime] = Field(
        column=Column(DateTime, server_default=func.now())
    )

    user: User = Relationship(back_populates='career_tracks')
    courses: List['CareerTrackCourse'] = Relationship(back_populates='career_track')


class CareerTrackCourse(SQLModel, table=True):
    __tablename__ = 'career_track_courses'

    id: Optional[int] = Field(default=None, primary_key=True)
    career_track_id: int = Field(foreign_key='career_tracks.id')
    course_id: int = Field(foreign_key='courses.id')
    order_index: int = Field(default=0)

    career_track: CareerTrack = Relationship(back_populates='courses')
    course: Course = Relationship(back_populates='career_track_courses')
