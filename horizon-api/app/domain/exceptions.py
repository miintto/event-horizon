class APIException(Exception):
    status_code: int = 500
    detail: str = "Server Error"


class UnauthorizedException(APIException):
    status_code = 401
    detail = "Unauthorized"


class InvalidCredentialsException(APIException):
    status_code = 401
    detail = "Invalid email or password"


class ForbiddenException(APIException):
    status_code = 403
    detail = "Permission denied"


class InactiveUserException(APIException):
    status_code = 403
    detail = "Account is deactivated"


class DuplicateEmailException(APIException):
    status_code = 409
    detail = "Email already registered"


class HostNotFoundException(APIException):
    status_code = 404
    detail = "Host not found"


class ContainerNotFoundException(APIException):
    status_code = 404
    detail = "Container not found"


class WorkloadNotFoundException(APIException):
    status_code = 404
    detail = "Workload not found"
