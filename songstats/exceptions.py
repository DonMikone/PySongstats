class APIError(Exception):
    """Base exception for all API errors"""

    def __init__(self, status_code, message):
        super().__init__(f"{status_code}: {message}")
        self.status_code = status_code
        self.message = message

    @classmethod
    def from_response(cls, response):
        return cls(response.status_code, response.json().get("message", "Unknown error"))


class BadRequest(APIError):
    """400 Bad Request"""
    pass


class Unauthorized(APIError):
    """401 Unauthorized"""
    pass


class Forbidden(APIError):
    """403 Forbidden"""
    pass


class NotFound(APIError):
    """404 Not Found"""
    pass


class RateLimitException(APIError):
    """429 Rate Limit Exceeded"""
    pass


class ServerError(APIError):
    """5xx Server Errors"""
    pass


error_map = {
    400: BadRequest,
    401: Unauthorized,
    403: Forbidden,
    404: NotFound,
    429: RateLimitException,
    500: ServerError,
    502: ServerError,
    503: ServerError,
}


class ParameterError(Exception):
    """Wrong parameters"""

    def __init__(self, message):
        super().__init__(f"{message}")
        self.message = message
