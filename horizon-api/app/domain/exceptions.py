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


class WorkloadRevisionNotFoundException(APIException):
    status_code = 404
    detail = "Workload revision not found"


class DuplicateWorkloadNameException(APIException):
    status_code = 409
    detail = "Workload name already exists"


class DeploymentNotFoundException(APIException):
    status_code = 404
    detail = "Deployment not found"


class DeploymentInProgressException(APIException):
    status_code = 409
    detail = "Deployment already in progress for this workload"


class RevisionRequiredException(APIException):
    status_code = 400
    detail = "Workload has no revision to deploy"


class SecretNotFoundException(APIException):
    status_code = 404
    detail = "Secret not found"


class DuplicateSecretNameException(APIException):
    status_code = 409
    detail = "Secret name already exists"


class SecretDecryptionException(APIException):
    status_code = 500
    detail = "Failed to decrypt secret"
