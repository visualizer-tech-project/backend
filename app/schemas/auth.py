import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole, AccountStatus


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
    status: AccountStatus = Field(..., description='Статус аккаунта')


class VerifyAccountRequest(BaseModel):
    code: uuid.UUID = Field(..., description='Код подтверждения из письма')


class ChangePasswordRequest(BaseModel):
    old_password: Optional[str] = Field(
        None, min_length=6, max_length=128, description='Старый пароль'
    )
    new_password: str = Field(
        ..., min_length=6, max_length=128, description='Новый пароль'
    )
    confirm_password: str = Field(
        ..., min_length=6, max_length=128, description='Подтверждение нового пароля'
    )


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description='Email для восстановления пароля')


class ResetPasswordRequest(BaseModel):
    code: uuid.UUID = Field(..., description='Код из письма для сброса пароля')
    new_password: str = Field(
        ..., min_length=6, max_length=128, description='Новый пароль'
    )
    confirm_password: str = Field(
        ..., min_length=6, max_length=128, description='Подтверждение нового пароля'
    )


class MessageResponse(BaseModel):
    message: str = Field(..., description='Сообщение о результате операции')
    success: bool = Field(default=True, description='Успешность операции')
