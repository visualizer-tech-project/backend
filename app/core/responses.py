from typing import Any, Dict

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