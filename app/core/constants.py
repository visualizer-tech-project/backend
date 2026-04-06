"""
Глобальные константы для приложения.
"""

# Пагинация
DEFAULT_SKIP = 0
DEFAULT_LIMIT = 20
MAX_LIMIT = 100
MIN_LIMIT = 1

# Роли пользователей
ROLE_ADMIN = 'admin'
ROLE_STUDENT = 'student'
ROLE_TEACHER = 'teacher'

# Типы курсов
COURSE_TYPE_REQUIRED = 'required'
COURSE_TYPE_ELECTIVE = 'elective'

# Статусы прогресса
PROGRESS_NOT_STARTED = 'not_started'
PROGRESS_IN_PROGRESS = 'in_progress'
PROGRESS_COMPLETED = 'completed'

# Операторы фильтрации
FILTER_OPERATOR_EQ = 'eq'
FILTER_OPERATOR_CONTAINS = 'contains'
FILTER_OPERATOR_STARTSWITH = 'startswith'
FILTER_OPERATOR_IEXACT = 'iexact'
