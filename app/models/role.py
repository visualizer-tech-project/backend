from typing import TYPE_CHECKING, List, Optional

from pydantic import computed_field
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseSQLModel, BaseModelSchema
from app.models.permission import RolePermissionMapping

if TYPE_CHECKING:
    from app.models.permission import Permission
    from app.models.user import User


class RoleBase(SQLModel):
    name: str = Field(max_length=100, unique=True, index=True)
    description: Optional[str] = Field(default=None, max_length=255)


class UserRoleMapping(SQLModel, table=True):
    __tablename__ = 'user_role'

    user_id: int = Field(foreign_key='users.id', primary_key=True)
    role_id: int = Field(foreign_key='roles.id', primary_key=True)


class Role(RoleBase, BaseSQLModel, table=True):
    __tablename__ = 'roles'

    permissions: List['Permission'] = Relationship(
        back_populates='roles',
        link_model=RolePermissionMapping,
        sa_relationship_kwargs={'lazy': 'selectin'},
    )

    users: List['User'] = Relationship(
        back_populates='roles',
        link_model=UserRoleMapping,
        sa_relationship_kwargs={'lazy': 'selectin'},
    )


class RolePublic(RoleBase, BaseModelSchema):
    @computed_field
    @property
    def scopes(self) -> list[str]:
        return [f'{p.subject}:{p.action}' for p in self.permissions]


class RoleCreate(RoleBase):
    scope_aliases: list[str] = []


class RoleUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    scope_aliases: Optional[list[str]] = None
