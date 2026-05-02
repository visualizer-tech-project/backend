from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core import exceptions
from app.core.responses import (
    BadRequestErrorSchema,
    ConflictErrorSchema,
    ForbiddenErrorSchema,
    InternalServerErrorSchema,
    NotFoundErrorSchema,
    UnauthorizedErrorSchema,
)
from app.core.logger import get_logger

logger = get_logger("exception_handlers")


async def not_found_exception_handler(request: Request, exc: exceptions.NotFoundError) -> JSONResponse:
    logger.warning(f"NotFoundError: {exc.detail}")
    return JSONResponse(status_code=404, content=NotFoundErrorSchema(detail=exc.detail).model_dump())


async def forbidden_exception_handler(request: Request, exc: exceptions.ForbiddenError) -> JSONResponse:
    logger.warning(f"ForbiddenError: {exc.detail}")
    return JSONResponse(status_code=403, content=ForbiddenErrorSchema(detail=exc.detail).model_dump())


async def unauthorized_exception_handler(request: Request, exc: exceptions.UnauthorizedError) -> JSONResponse:
    logger.warning(f"UnauthorizedError: {exc.detail}")
    return JSONResponse(status_code=401, content=UnauthorizedErrorSchema(detail=exc.detail).model_dump())


async def bad_request_exception_handler(request: Request, exc: exceptions.BadRequestError) -> JSONResponse:
    logger.warning(f"BadRequestError: {exc.detail}")
    return JSONResponse(status_code=400, content=BadRequestErrorSchema(detail=exc.detail).model_dump())


async def conflict_exception_handler(request: Request, exc: exceptions.ConflictError) -> JSONResponse:
    logger.warning(f"ConflictError: {exc.detail}")
    return JSONResponse(status_code=409, content=ConflictErrorSchema(detail=exc.detail).model_dump())


async def internal_server_error_exception_handler(request: Request, exc: exceptions.InternalServerError) -> JSONResponse:
    logger.error(f"InternalServerError: {exc.detail}", exc_info=True)
    return JSONResponse(status_code=500, content=InternalServerErrorSchema(detail=exc.detail).model_dump())


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.warning(f"ValidationError: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )


def register_exception_handlers(app):
    app.add_exception_handler(exceptions.NotFoundError, not_found_exception_handler)
    app.add_exception_handler(exceptions.ForbiddenError, forbidden_exception_handler)
    app.add_exception_handler(exceptions.UnauthorizedError, unauthorized_exception_handler)
    app.add_exception_handler(exceptions.BadRequestError, bad_request_exception_handler)
    app.add_exception_handler(exceptions.ConflictError, conflict_exception_handler)
    app.add_exception_handler(exceptions.InternalServerError, internal_server_error_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
