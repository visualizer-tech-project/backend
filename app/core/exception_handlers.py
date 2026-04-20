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


async def not_found_exception_handler(
    request: Request,
    exc: exceptions.NotFoundError
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content=NotFoundErrorSchema(detail=exc.detail).model_dump()
    )


async def forbidden_exception_handler(
    request: Request,
    exc: exceptions.ForbiddenError
) -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content=ForbiddenErrorSchema(detail=exc.detail).model_dump()
    )


async def unauthorized_exception_handler(
    request: Request,
    exc: exceptions.UnauthorizedError
) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content=UnauthorizedErrorSchema(detail=exc.detail).model_dump()
    )


async def bad_request_exception_handler(
    request: Request,
    exc: exceptions.BadRequestError
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content=BadRequestErrorSchema(detail=exc.detail).model_dump()
    )


async def conflict_exception_handler(
    request: Request,
    exc: exceptions.ConflictError
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content=ConflictErrorSchema(detail=exc.detail).model_dump()
    )


async def internal_server_error_exception_handler(
    request: Request,
    exc: exceptions.InternalServerError
) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=InternalServerErrorSchema(detail=exc.detail).model_dump()
    )


def register_exception_handlers(app):
    app.add_exception_handler(exceptions.NotFoundError, not_found_exception_handler)
    app.add_exception_handler(exceptions.ForbiddenError, forbidden_exception_handler)
    app.add_exception_handler(exceptions.UnauthorizedError, unauthorized_exception_handler)
    app.add_exception_handler(exceptions.BadRequestError, bad_request_exception_handler)
    app.add_exception_handler(exceptions.ConflictError, conflict_exception_handler)
    app.add_exception_handler(exceptions.InternalServerError, internal_server_error_exception_handler)
