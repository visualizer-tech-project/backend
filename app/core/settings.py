from functools import lru_cache

from pydantic import BaseModel, EmailStr, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DbSettings(BaseSettings):
    schema: str = 'postgresql+asyncpg'
    host: str = 'localhost'
    user: str = 'postgres'
    password: str = 'pass'
    port: int = 5432
    name: str = 'db'

    model_config = SettingsConfigDict(
        env_file='.env',
        env_prefix='DB_',
        extra='ignore',
    )


class AuthSettings(BaseModel):
    jwt_secret_key: str = 'your-secret-key-min-32-chars-long-here!!!'
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7


class RBACSettings(BaseModel):
    admin_email: EmailStr = 'admin@example.com'
    admin_password: str = 'admin123'
    admin_first_name: str = 'Admin'
    admin_last_name: str = 'User'
    admin_role: str = 'admin'
    public_role: str = 'public'


class EmailSettings(BaseModel):
    username: EmailStr = 'test@example.com'
    password: SecretStr = 'your-password'
    title: str = 'EduMap'
    port: int = 587
    server: str = 'smtp.gmail.com'
    notification_lifetime_seconds: int = 3600
    templates_dir: str = 'templates'
    base_url: str = 'http://localhost:8000'


class Settings(BaseSettings):
    db: DbSettings = DbSettings()
    auth: AuthSettings = AuthSettings()
    rbac: RBACSettings = RBACSettings()
    email: EmailSettings = EmailSettings()

    model_config = SettingsConfigDict(
        env_file='.env',
        env_nested_delimiter='__',
        extra='ignore',
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()