from typing import Annotated

from fastapi import Security

from app.core.security import get_current_user
from app.models.user import User

CurrentUser = Annotated[User, Security(get_current_user)]