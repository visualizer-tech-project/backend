from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies import get_auth_service
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserPublic
from app.services.auth import AuthService

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post(
    '/register',
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary='Регистрация нового пользователя',
    responses={
        400: {'description': 'Некорректные данные'},
        409: {'description': 'Email уже зарегистрирован'},
        500: {'description': 'Внутренняя ошибка сервера'},
    },
)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserPublic:
    """
    Регистрация нового пользователя.

    - **email**: Email пользователя
    - **password**: Пароль
    - **first_name**: Имя
    - **last_name**: Фамилия
    """
    try:
        return await auth_service.register(user_data)
    except ValueError as e:
        if 'already exists' in str(e):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    '/login',
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary='Вход в систему',
    responses={
        401: {'description': 'Неверный email или пароль'},
        500: {'description': 'Внутренняя ошибка сервера'},
    },
)
async def login(
    login_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    """
    Вход в систему.

    - **username**: Email пользователя
    - **password**: Пароль
    """
    try:
        from app.schemas.user import LoginRequest

        login_request = LoginRequest(
            email=login_data.username, password=login_data.password
        )
        return await auth_service.login(login_request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
