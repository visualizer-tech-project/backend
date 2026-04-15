import uuid
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, computed_field
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.role import Role


class PermissionBase(SQLModel):
    subject: str = Field(max_length=100)
    action: str = Field(max_length=100)


class Permission(PermissionBase, table=True):
    __tablename__ = 'permissions'

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: Optional[str] = Field(default=None)
    updated_at: Optional[str] = Field(default=None)

    roles: List['Role'] = Relationship(
        back_populates='permissions',
        link_model='role_permission'
    )


class PermissionWithAlias(PermissionBase):
    id: uuid.UUID
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @computed_field
    @property
    def alias(self) -> str:
        return f'{self.subject}:{self.action}'


class PermissionPublic(BaseModel, PermissionWithAlias):
    pass


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(PermissionBase):
    subject: Optional[str] = None
    action: Optional[str] = None

class RolePermissionMapping(SQLModel, table=True):
    __tablename__ = 'role_permission'

    role_id: uuid.UUID = Field(foreign_key='role.id', primary_key=True)
    permission_id: uuid.UUID = Field(foreign_key='permissions.id', primary_key=True)