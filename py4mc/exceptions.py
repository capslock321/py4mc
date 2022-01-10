class ApiException(Exception):
    pass


class ResourceNotFound(ApiException):
    pass


class InternalServerException(ApiException):
    pass


class UserNotFound(ApiException):
    pass


class Ratelimited(ApiException):
    pass

class InvalidMetric(ApiException):
    pass
