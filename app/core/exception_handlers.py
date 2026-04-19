from fastapi import Request
from fastapi.responses import JSONResponse

from app.core import exceptions
from app.core.responses import (
    BadRequestErrorSchema,
    ConflictErrorSchema,
    ForbiddenErrorSchema,
    InternalServerErrorSchema,
    NotFoundErrorSchema,
    UnauthorizedErrorSchema,
)

EXCEPTION_MAPPING = {
    exceptions.NotFoundError: (404, NotFoundErrorSchema),
    exceptions.ForbiddenError: (403, ForbiddenErrorSchema),
    exceptions.UnauthorizedError: (401, UnauthorizedErrorSchema),
    exceptions.BadRequestError: (400, BadRequestErrorSchema),
    exceptions.ConflictError: (409, ConflictErrorSchema),
    exceptions.InternalServerError: (500, InternalServerErrorSchema),
}


async def generic_exception_handler(
    request: Request,
    exc: exceptions.AppBaseException,
) -> JSONResponse:
    status_code, schema_class = EXCEPTION_MAPPING.get(
        type(exc),
        (500, InternalServerErrorSchema)
    )
    return JSONResponse(
        status_code=status_code,
        content=schema_class(detail=exc.detail).model_dump()
    )


def register_exception_handlers(app):
    for exc_class in EXCEPTION_MAPPING.keys():
        app.add_exception_handler(exc_class, generic_exception_handler)
