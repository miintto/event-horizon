class APIException(Exception):
    status_code: int = 500
    detail: str = "Server Error"


class UnauthorizedException(APIException):
    status_code = 401
    detail = "Unauthorized"


class HostNotFoundException(APIException):
    status_code = 404
    detail = "Host not found"


class ContainerNotFoundException(APIException):
    status_code = 404
    detail = "Container not found"
