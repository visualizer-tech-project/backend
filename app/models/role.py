import uuid
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, computed_field
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.permission import Permission
    from app.models.user import User


class RoleBase(SQLModel):
    name: str = Field(max_length=100, unique=True, index=True)
    description: Optional[str] = Field(default=None, max_length=255)


class Role(RoleBase, table=True):
    __tablename__ = 'roles'

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: Optional[str] = Field(default=None)
    updated_at: Optional[str] = Field(default=None)

    permissions: List['Permission'] = Relationship(
        back_populates='roles',
        link_model='role_permission',
        sa_relationship_kwargs={'lazy': 'selectin'},
    )

    users: List['User'] = Relationship(
        back_populates='roles',
        link_model='user_role',
        sa_relationship_kwargs={'lazy': 'selectin'},
    )


class RoleWithScopes(RoleBase):
    id: uuid.UUID

    @computed_field
    @property
    def scopes(self) -> list[str]:
        return list(map(lambda permission: f'{permission.subject}:{permission.action}', self.permissions))


class RolePublic(BaseModel, RoleWithScopes):
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class RoleChange(RoleBase):
    scope_aliases: list[str] = []


class RoleCreate(RoleChange):
    pass


class RoleUpdate(RoleChange):
    name: Optional[str] = None
    description: Optional[str] = None

class UserRoleMapping(SQLModel, table=True):
    __tablename__ = 'user_role'

    user_id: int = Field(foreign_key='users.id', primary_key=True)
    role_id: uuid.UUID = Field(foreign_key='roles.id', primary_key=True)