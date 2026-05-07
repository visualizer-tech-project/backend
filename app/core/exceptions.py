class AppBaseException(Exception):
    def __init__(self, detail: str = 'An error occurred'):
        self.detail = detail
        super().__init__(detail)


class NotFoundError(AppBaseException):
    pass


class ForbiddenError(AppBaseException):
    def __init__(self, detail: str = 'Not enough permissions'):
        super().__init__(detail)


class UnauthorizedError(AppBaseException):
    def __init__(self, detail: str = 'Not authenticated'):
        super().__init__(detail)


class BadRequestError(AppBaseException):
    def __init__(self, detail: str = 'Bad request'):
        super().__init__(detail)


class ConflictError(AppBaseException):
    def __init__(self, detail: str = 'Resource already exists'):
        super().__init__(detail)


class InternalServerError(AppBaseException):
    def __init__(self, detail: str = 'Internal server error'):
        super().__init__(detail)
