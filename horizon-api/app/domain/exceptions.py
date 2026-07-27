class APIException(Exception):
    status_code: int = 500
    detail: str = "Server Error"


class HostNotFoundException(APIException):
    status_code = 404
    detail = "Host not found"


class ContainerNotFoundException(APIException):
    status_code = 404
    detail = "Container not found"
