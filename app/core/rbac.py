from app.core.settings import settings

INITIAL_SUBJECTS = ['profile', 'programs', 'courses', 'career_tracks', 'progress', 'roles', 'permissions']

INITIAL_ACTIONS = ['read', 'create', 'update', 'delete', 'list']

INITIAL_PERMISSION_SCHEMA: dict[str, list[str]] = {
    settings.rbac.admin_role: [],
    settings.rbac.public_role: ['profile:read'],
    'teacher': [
        'profile:read',
        'programs:list', 'programs:read', 'programs:create', 'programs:update',
        'courses:list', 'courses:read', 'courses:create', 'courses:update',
        'career_tracks:list', 'career_tracks:read', 'career_tracks:create', 'career_tracks:update',
        'progress:list', 'progress:read', 'progress:create', 'progress:update', 'progress:view_any', 'progress:modify_any',
    ],
    'student': [
        'profile:read',
        'programs:list', 'programs:read',
        'courses:list', 'courses:read',
        'career_tracks:list', 'career_tracks:read',
        'progress:list', 'progress:read',
    ],
}

PERMISSION_DESCRIPTIONS: dict[str, str] = {
    'profile:read': 'Просмотр своего профиля',
    'profile:update': 'Обновление своего профиля',
    'profile:list': 'Просмотр списка пользователей',
    'profile:detail': 'Просмотр деталей пользователя',
    'programs:list': 'Просмотр списка программ',
    'programs:read': 'Просмотр программы',
    'programs:create': 'Создание программы',
    'programs:update': 'Обновление программы',
    'programs:delete': 'Удаление программы',
    'courses:list': 'Просмотр списка курсов',
    'courses:read': 'Просмотр курса',
    'courses:create': 'Создание курса',
    'courses:update': 'Обновление курса',
    'courses:delete': 'Удаление курса',
    'career_tracks:list': 'Просмотр списка карьерных треков',
    'career_tracks:read': 'Просмотр карьерного трека',
    'career_tracks:create': 'Создание карьерного трека',
    'career_tracks:update': 'Обновление карьерного трека',
    'career_tracks:delete': 'Удаление карьерного трека',
    'progress:list': 'Просмотр прогресса',
    'progress:read': 'Просмотр деталей прогресса',
    'progress:create': 'Создание записи прогресса',
    'progress:update': 'Обновление прогресса',
    'progress:delete': 'Удаление прогресса',
    'progress:view_any': 'Просмотр прогресса любого пользователя',
    'progress:modify_any': 'Изменение прогресса любого пользователя',
    'roles:list': 'Просмотр списка ролей',
    'roles:read': 'Просмотр роли',
    'roles:create': 'Создание роли',
    'roles:update': 'Обновление роли',
    'roles:delete': 'Удаление роли',
    'permissions:list': 'Просмотр списка разрешений',
    'permissions:read': 'Просмотр разрешения',
}