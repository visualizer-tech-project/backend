from typing import Any, Dict, List, Optional

from sqlmodel import and_, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.course import Course
from app.models.user import User
from app.models.userprogress import (
    UserProgress,
    UserProgressStatus,
    get_current_datetime,
)
from app.repositories.base import BaseRepository
from app.repositories.course import CourseRepository
from app.schemas.userprogress import (
    ProgressCreate,
    ProgressUpdate,
    UserProgressWithDetails,
)

GRADE_EXCELLENT = 90
GRADE_GOOD = 75
GRADE_SATISFACTORY = 60


class UserProgressRepository(
    BaseRepository[UserProgress, ProgressCreate, ProgressUpdate]
):
    def __init__(self, session: AsyncSession):
        super().__init__(UserProgress, session)

    async def get_by_user_and_course(
        self,
        user_id: int,
        course_id: int,
    ) -> Optional[UserProgress]:
        """Получить прогресс пользователя по курсу"""
        query = select(UserProgress).where(
            and_(UserProgress.user_id == user_id, UserProgress.course_id == course_id)
        )
        result = await self.session.exec(query)
        return result.first()

    async def get_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        status: Optional[UserProgressStatus] = None,
        program_id: Optional[int] = None,
    ) -> tuple[List[UserProgress], int]:
        """Получить прогресс пользователя по всем курсам с фильтрацией"""
        base_query = select(UserProgress).where(UserProgress.user_id == user_id)

        if status:
            base_query = base_query.where(UserProgress.status == status)

        if program_id:
            base_query = base_query.join(Course).where(Course.program_id == program_id)

        count_query = select(func.count()).select_from(base_query.subquery())
        total = await self.session.scalar(count_query) or 0

        query = (
            base_query.offset(skip)
            .limit(limit)
            .order_by(UserProgress.updated_at.desc())
        )
        result = await self.session.exec(query)
        items = result.all()

        return items, total

    async def get_by_course(
        self,
        course_id: int,
        skip: int = 0,
        limit: int = 20,
        status: Optional[UserProgressStatus] = None,
    ) -> tuple[List[UserProgress], int]:
        """Получить прогресс всех пользователей по курсу"""
        filters = {'course_id': course_id}
        if status:
            filters['status'] = status

        return await self.get_all(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by='updated_at',
            descending=True,
        )

    async def create_or_update(
        self,
        progress_data: ProgressCreate,
    ) -> UserProgress:
        """Создать или обновить запись прогресса"""
        existing = await self.get_by_user_and_course(
            progress_data.user_id, progress_data.course_id
        )

        if existing:
            update_dict = progress_data.model_dump(exclude_unset=True)
            update_dict.pop('user_id', None)
            update_dict.pop('course_id', None)

            update_dict = self._auto_set_dates_on_update(
                existing, update_dict, progress_data.status
            )

            for field, value in update_dict.items():
                setattr(existing, field, value)

            self.session.add(existing)
            await self.session.commit()
            await self.session.refresh(existing)
            return existing
        create_dict = progress_data.model_dump()

        create_dict = self._auto_set_dates_on_create(create_dict, progress_data.status)

        new_progress = UserProgress(**create_dict)
        self.session.add(new_progress)
        await self.session.commit()
        await self.session.refresh(new_progress)
        return new_progress

    def _auto_set_dates_on_create(
        self, create_dict: dict, status: UserProgressStatus
    ) -> dict:
        """Автоматическая установка дат при создании"""
        current_time = get_current_datetime()

        if status == UserProgressStatus.IN_PROGRESS:
            if not create_dict.get('started_at'):
                create_dict['started_at'] = current_time

        elif status == UserProgressStatus.COMPLETED:
            if not create_dict.get('started_at'):
                create_dict['started_at'] = current_time
            if not create_dict.get('completed_at'):
                create_dict['completed_at'] = current_time

            if (
                create_dict.get('started_at')
                and create_dict.get('completed_at')
                and create_dict['completed_at'] < create_dict['started_at']
            ):
                raise ValueError('completed_at не может быть раньше started_at')

        return create_dict

    def _auto_set_dates_on_update(
        self, existing: UserProgress, update_dict: dict, status: UserProgressStatus
    ) -> dict:
        """Автоматическая установка дат при обновлении"""
        current_time = get_current_datetime()

        if status == UserProgressStatus.IN_PROGRESS:
            if not existing.started_at and 'started_at' not in update_dict:
                update_dict['started_at'] = current_time

        elif status == UserProgressStatus.COMPLETED:
            if not existing.completed_at and 'completed_at' not in update_dict:
                update_dict['completed_at'] = current_time
            if not existing.started_at and 'started_at' not in update_dict:
                update_dict['started_at'] = current_time

        started_at = update_dict.get('started_at', existing.started_at)
        completed_at = update_dict.get('completed_at', existing.completed_at)

        if started_at and completed_at and completed_at < started_at:
            raise ValueError('completed_at не может быть раньше started_at')

        return update_dict

    async def update_status(
        self,
        user_id: int,
        course_id: int,
        status: UserProgressStatus,
        grade: Optional[int] = None,
    ) -> Optional[UserProgress]:
        """Обновить статус прогресса"""
        progress_data = ProgressCreate(
            user_id=user_id,
            course_id=course_id,
            status=status,
            grade=grade,
        )

        return await self.create_or_update(progress_data)

    async def mark_completed(
        self,
        user_id: int,
        course_id: int,
        grade: Optional[int] = None,
    ) -> Optional[UserProgress]:
        """Отметить курс как завершенный"""
        return await self.update_status(
            user_id=user_id,
            course_id=course_id,
            status=UserProgressStatus.COMPLETED,
            grade=grade,
        )

    async def mark_in_progress(
        self,
        user_id: int,
        course_id: int,
    ) -> Optional[UserProgress]:
        """Отметить курс как начатый"""
        return await self.update_status(
            user_id=user_id,
            course_id=course_id,
            status=UserProgressStatus.IN_PROGRESS,
        )

    async def get_user_stats(
        self,
        user_id: int,
        program_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Получить статистику прогресса пользователя"""
        progresses, _ = await self.get_by_user(
            user_id=user_id,
            program_id=program_id,
            skip=0,
            limit=10000,
        )

        total = len(progresses)
        completed = sum(
            1 for p in progresses if p.status == UserProgressStatus.COMPLETED
        )
        in_progress = sum(
            1 for p in progresses if p.status == UserProgressStatus.IN_PROGRESS
        )
        not_started = sum(
            1 for p in progresses if p.status == UserProgressStatus.NOT_STARTED
        )

        grades = [
            p.grade
            for p in progresses
            if p.status == UserProgressStatus.COMPLETED and p.grade is not None
        ]
        average_grade = sum(grades) / len(grades) if grades else None

        return {
            'total_courses': total,
            'completed_courses': completed,
            'in_progress_courses': in_progress,
            'not_started_courses': not_started,
            'completion_percentage': round((completed / total * 100), 2)
            if total > 0
            else 0,
            'average_grade': round(average_grade, 2) if average_grade else None,
        }

    async def get_program_stats(
        self,
        program_id: int,
    ) -> Dict[str, Any]:
        """Получить статистику прогресса по программе"""
        courses_query = select(Course).where(Course.program_id == program_id)
        courses_result = await self.session.exec(courses_query)
        courses = courses_result.all()
        course_ids = [c.id for c in courses]

        if not course_ids:
            return {
                'total_students': 0,
                'total_courses': 0,
                'average_completion_rate': 0,
                'courses_stats': [],
            }

        students_query = select(UserProgress.user_id.distinct()).where(
            UserProgress.course_id.in_(course_ids)
        )
        students_result = await self.session.exec(students_query)
        student_ids = students_result.all()
        total_students = len(student_ids)

        all_progress_query = select(UserProgress).where(
            UserProgress.course_id.in_(course_ids)
        )
        all_progress_result = await self.session.exec(all_progress_query)
        all_progress = all_progress_result.all()

        progress_by_course = {course_id: [] for course_id in course_ids}
        for progress in all_progress:
            progress_by_course[progress.course_id].append(progress)

        courses_stats = []
        for course in courses:
            progresses = progress_by_course.get(course.id, [])
            total = len(progresses)
            completed = sum(
                1 for p in progresses if p.status == UserProgressStatus.COMPLETED
            )
            in_progress = sum(
                1 for p in progresses if p.status == UserProgressStatus.IN_PROGRESS
            )

            grades = [
                p.grade
                for p in progresses
                if p.status == UserProgressStatus.COMPLETED and p.grade is not None
            ]
            average_grade = sum(grades) / len(grades) if grades else None

            courses_stats.append(
                {
                    'course_id': course.id,
                    'course_title': course.title,
                    'total_students': total,
                    'completed_students': completed,
                    'completion_rate': round((completed / total * 100), 2)
                    if total > 0
                    else 0,
                    'average_grade': round(average_grade, 2) if average_grade else None,
                    'in_progress_students': in_progress,
                }
            )

        avg_completion_rate = (
            sum(cs['completion_rate'] for cs in courses_stats) / len(courses_stats)
            if courses_stats
            else 0
        )

        return {
            'program_id': program_id,
            'total_students': total_students,
            'total_courses': len(courses),
            'average_completion_rate': round(avg_completion_rate, 2),
            'courses_stats': courses_stats,
        }

    async def get_user_progress_with_details(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        status: Optional[UserProgressStatus] = None,
        program_id: Optional[int] = None,
    ) -> tuple[List[UserProgressWithDetails], int]:
        """Получить прогресс пользователя с деталями курсов"""
        base_query = select(UserProgress).where(UserProgress.user_id == user_id)

        if status:
            base_query = base_query.where(UserProgress.status == status)

        if program_id:
            base_query = base_query.join(Course).where(Course.program_id == program_id)

        count_query = select(func.count()).select_from(base_query.subquery())
        total = await self.session.scalar(count_query) or 0

        query = (
            base_query.offset(skip)
            .limit(limit)
            .order_by(UserProgress.updated_at.desc())
        )
        result = await self.session.exec(query)
        progresses = result.all()

        if not progresses:
            return [], total

        course_ids = list({p.course_id for p in progresses})
        courses_query = select(Course).where(Course.id.in_(course_ids))
        courses_result = await self.session.exec(courses_query)
        courses = {c.id: c for c in courses_result.all()}

        details_list = []
        for progress in progresses:
            course = courses.get(progress.course_id)
            if course:
                details_list.append(
                    UserProgressWithDetails(
                        id=progress.id,
                        user_id=progress.user_id,
                        course_id=progress.course_id,
                        status=UserProgressStatus(progress.status.value),
                        grade=progress.grade,
                        started_at=progress.started_at,
                        completed_at=progress.completed_at,
                        updated_at=progress.updated_at,
                        course_title=course.title,
                        course_type=course.type if hasattr(course, 'type') else None,
                        program_id=course.program_id,
                    )
                )

        return details_list, total

    async def get_course_completion_stats(
        self,
        course_id: int,
    ) -> Dict[str, Any]:
        """Получить статистику завершения курса"""
        query = select(UserProgress).where(UserProgress.course_id == course_id)
        result = await self.session.exec(query)
        progresses = result.all()

        total = len(progresses)
        completed = sum(
            1 for p in progresses if p.status == UserProgressStatus.COMPLETED
        )
        in_progress = sum(
            1 for p in progresses if p.status == UserProgressStatus.IN_PROGRESS
        )
        not_started = sum(
            1 for p in progresses if p.status == UserProgressStatus.NOT_STARTED
        )

        grade_distribution = {
            'excellent': 0,
            'good': 0,
            'satisfactory': 0,
            'bad': 0,
        }

        for p in progresses:
            if p.status == UserProgressStatus.COMPLETED and p.grade is not None:
                if p.grade >= GRADE_EXCELLENT:
                    grade_distribution['excellent'] += 1
                elif p.grade >= GRADE_GOOD:
                    grade_distribution['good'] += 1
                elif p.grade >= GRADE_SATISFACTORY:
                    grade_distribution['satisfactory'] += 1
                else:
                    grade_distribution['bad'] += 1

        return {
            'course_id': course_id,
            'total_students': total,
            'completed_students': completed,
            'in_progress_students': in_progress,
            'not_started_students': not_started,
            'completion_rate': round((completed / total * 100), 2) if total > 0 else 0,
            'grade_distribution': grade_distribution,
        }

    async def bulk_create_or_update(
        self,
        progress_data_list: List[ProgressCreate],
    ) -> List[UserProgress]:
        """Массовое создание или обновление записей прогресса"""
        results = []
        for progress_data in progress_data_list:
            progress = await self.create_or_update(progress_data)
            results.append(progress)
        return results

    async def get_students_progress_summary(
        self,
        program_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Dict[str, Any]], int]:
        """Получить сводку прогресса студентов программы"""
        courses_query = select(Course).where(Course.program_id == program_id)
        courses_result = await self.session.exec(courses_query)
        courses = courses_result.all()
        course_ids = [c.id for c in courses]

        if not course_ids:
            return [], 0

        students_query = select(UserProgress.user_id.distinct()).where(
            UserProgress.course_id.in_(course_ids)
        )
        students_result = await self.session.exec(students_query)
        all_student_ids = students_result.all()
        total_students = len(all_student_ids)

        paginated_student_ids = all_student_ids[skip : skip + limit]
        if not paginated_student_ids:
            return [], total_students

        users_query = select(User).where(User.id.in_(paginated_student_ids))
        users_result = await self.session.exec(users_query)
        users = {u.id: u for u in users_result.all()}

        progress_query = select(UserProgress).where(
            and_(
                UserProgress.user_id.in_(paginated_student_ids),
                UserProgress.course_id.in_(course_ids),
            )
        )
        progress_result = await self.session.exec(progress_query)
        all_progress = progress_result.all()

        progress_by_student = {student_id: [] for student_id in paginated_student_ids}
        for progress in all_progress:
            progress_by_student[progress.user_id].append(progress)

        students_progress = []
        total_courses_count = len(course_ids)

        for student_id in paginated_student_ids:
            user = users.get(student_id)
            if not user:
                continue

            student_progress = progress_by_student.get(student_id, [])
            completed = sum(
                1 for p in student_progress if p.status == UserProgressStatus.COMPLETED
            )

            last_activity = None
            if student_progress:
                last_activity = max(p.updated_at for p in student_progress)

            students_progress.append(
                {
                    'user_id': student_id,
                    'user_name': f'{user.first_name} {user.last_name}'
                    if user.first_name
                    else user.email,
                    'user_email': user.email,
                    'total_courses': total_courses_count,
                    'completed_courses': completed,
                    'completion_percentage': round(
                        (completed / total_courses_count * 100), 2
                    )
                    if total_courses_count > 0
                    else 0,
                    'last_activity': last_activity,
                }
            )

        students_progress.sort(key=lambda x: x['completion_percentage'], reverse=True)

        return students_progress, total_students

    async def get_user_learning_path(
        self,
        user_id: int,
        program_id: int,
    ) -> Dict[str, Any]:
        """Получить учебный путь пользователя"""
        course_repo = CourseRepository(self.session)

        courses_query = (
            select(Course).where(Course.program_id == program_id).order_by(Course.title)
        )  # убрал semester
        courses_result = await self.session.exec(courses_query)
        all_courses = courses_result.all()

        available_courses, _ = await course_repo.get_available_for_user(
            user_id=user_id,
            program_id=program_id,
            skip=0,
            limit=len(all_courses) or 1000,
        )
        available_course_ids = {c.id for c in available_courses}

        completed_progress, _ = await self.get_by_user(
            user_id=user_id,
            status=UserProgressStatus.COMPLETED,
            program_id=program_id,
        )
        completed_course_ids = {p.course_id for p in completed_progress}

        in_progress_progress, _ = await self.get_by_user(
            user_id=user_id,
            status=UserProgressStatus.IN_PROGRESS,
            program_id=program_id,
        )
        in_progress_course_ids = {p.course_id for p in in_progress_progress}

        courses_with_status = []
        for course in all_courses:
            if course.id in completed_course_ids:
                status = 'completed'
            elif course.id in in_progress_course_ids:
                status = 'in_progress'
            elif course.id in available_course_ids:
                status = 'available'
            else:
                status = 'locked'

            courses_with_status.append(
                {
                    'id': course.id,
                    'title': course.title,
                    'type': course.type if hasattr(course, 'type') else None,
                    'status': status,
                }
            )

        return {
            'user_id': user_id,
            'program_id': program_id,
            'courses': courses_with_status,
            'total_courses': len(all_courses),
            'completed_courses': len(completed_course_ids),
            'in_progress_courses': len(in_progress_course_ids),
            'available_courses': len(available_course_ids),
        }
