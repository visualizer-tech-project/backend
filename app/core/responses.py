from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from pydantic import BaseModel


class ErrorSchema(BaseModel):
    detail: str


class InternalServerErrorSchema(ErrorSchema):
    pass


class UnauthorizedErrorSchema(ErrorSchema):
    pass


class ForbiddenErrorSchema(ErrorSchema):
    pass


class NotFoundErrorSchema(ErrorSchema):
    pass


class BadRequestErrorSchema(ErrorSchema):
    pass


class ConflictErrorSchema(ErrorSchema):
    pass


common_responses: Dict[int, Dict[str, Any]] = {
    500: {
        'model': InternalServerErrorSchema,
        'description': 'Internal server error'
    }
}

auth_responses: Dict[int, Dict[str, Any]] = {
    401: {
        'model': UnauthorizedErrorSchema,
        'description': 'Not authenticated'
    },
    403: {
        'model': ForbiddenErrorSchema,
        'description': 'Not enough permissions'
    },
}

detail_responses: Dict[int, Dict[str, Any]] = {
    404: {
        'model': NotFoundErrorSchema,
        'description': 'Resource not found'
    }
}

bad_request_responses: Dict[int, Dict[str, Any]] = {
    400: {
        'model': BadRequestErrorSchema,
        'description': 'Bad request'
    }
}

conflict_responses: Dict[int, Dict[str, Any]] = {
    409: {
        'model': ConflictErrorSchema,
        'description': 'Resource already exists'
    }
}


def raise_forbidden(detail: str = 'Not enough permissions') -> None:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail
    )


def raise_unauthorized(detail: str = 'Not authenticated') -> None:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail
    )


def raise_not_found(resource: str = 'Resource', detail: Optional[str] = None) -> None:
    message = detail or f'{resource} not found'
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=message
    )


def raise_bad_request(detail: str = 'Bad request') -> None:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail
    )


def raise_conflict(detail: str = 'Resource already exists') -> None:
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=detail
    )