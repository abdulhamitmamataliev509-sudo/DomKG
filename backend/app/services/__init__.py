class ServiceError(Exception):
    """Simple service-layer exception with HTTP-compatible metadata."""

    def __init__(self, message, status_code=400, code="ERROR", details=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or {}
