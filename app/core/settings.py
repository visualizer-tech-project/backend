from functools import lru_cache

from pydantic import BaseModel, EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DbSettings(BaseModel):
    schema: str = 'postgresql+asyncpg'
    host: str = 'localhost'
    user: str = 'postgres'
    password: str = 'pass'
    port: int = 5432
    name: str = 'db'


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


class Settings(BaseSettings):
    db: DbSettings = DbSettings()
    auth: AuthSettings = AuthSettings()
    rbac: RBACSettings = RBACSettings()

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