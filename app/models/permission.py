from typing import TYPE_CHECKING, List, Optional

from pydantic import computed_field
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseSQLModel, BaseModelSchema

if TYPE_CHECKING:
    from app.models.role import Role


class PermissionBase(SQLModel):
    subject: str = Field(max_length=100)
    action: str = Field(max_length=100)

class RolePermissionMapping(SQLModel, table=True):
    __tablename__ = 'role_permission'

    role_id: int = Field(foreign_key='roles.id', primary_key=True)
    permission_id: int = Field(foreign_key='permissions.id', primary_key=True)


class Permission(PermissionBase, BaseSQLModel, table=True):
    __tablename__ = 'permissions'

    roles: List['Role'] = Relationship(
        back_populates='permissions',
        link_model=RolePermissionMapping
    )


class PermissionPublic(PermissionBase, BaseModelSchema):

    @computed_field
    @property
    def alias(self) -> str:
        return f'{self.subject}:{self.action}'


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(SQLModel):
    subject: Optional[str] = None
    action: Optional[str] = None
