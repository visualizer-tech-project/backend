from pydantic import BaseModel, EmailStr, Field, computed_field

from app.models.user import UserRole


class AuthBase(BaseModel):
    email: EmailStr = Field(..., description='Email пользователя')
    password: str = Field(..., min_length=6, max_length=128, description='Пароль')


class LoginRequest(AuthBase):
    pass


class RegisterRequest(AuthBase):
    first_name: str = Field(..., min_length=1, max_length=100, description='Имя')
    last_name: str = Field(..., min_length=1, max_length=100, description='Фамилия')


class TokenBase(BaseModel):
    access_token: str = Field(..., description='JWT access token')
    refresh_token: str = Field(..., description='JWT refresh token')
    token_type: str = Field(default='bearer', description='Тип токена')


class TokenResponse(TokenBase):
    pass


class RefreshResponse(TokenBase):
    pass


class LogoutResponse(BaseModel):
    success: bool = Field(..., description='Успешность операции')


class UserInfoBase(BaseModel):
    id: int = Field(..., description='ID пользователя')
    email: EmailStr = Field(..., description='Email пользователя')
    first_name: str = Field(..., description='Имя')
    last_name: str = Field(..., description='Фамилия')


class MeResponse(UserInfoBase):
    role: UserRole = Field(..., description='Роль пользователя')