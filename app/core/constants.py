"""
Глобальные константы для приложения.
"""
from datetime import timedelta

# Пагинация
DEFAULT_SKIP = 0
DEFAULT_LIMIT = 20
MAX_LIMIT = 100
MIN_LIMIT = 1

# Операторы фильтрации
FILTER_OPERATOR_EQ = 'eq'
FILTER_OPERATOR_CONTAINS = 'contains'
FILTER_OPERATOR_STARTSWITH = 'startswith'
FILTER_OPERATOR_IEXACT = 'iexact'

TITLE_MAX_LENGTH = 255
TITLE_FIELD_CONFIG = {"min_length": 1, "max_length": TITLE_MAX_LENGTH}

# JWT и Cookies
REFRESH_TOKEN_COOKIE_NAME = 'refresh_token'
REFRESH_TOKEN_COOKIE_MAX_AGE = int(timedelta(days=7).total_seconds())
