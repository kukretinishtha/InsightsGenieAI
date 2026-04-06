"""Custom exceptions for InsightGenie AI application."""

from typing import Any, Dict, Optional


class InsightGenieException(Exception):
    """Base exception for InsightGenie AI."""
    
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize exception."""
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(InsightGenieException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=400,
            details=details
        )


class NotFoundError(InsightGenieException):
    """Raised when a resource is not found."""
    
    def __init__(self, message: str, resource: Optional[str] = None):
        details = {"resource": resource} if resource else {}
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404,
            details=details
        )


class AuthenticationError(InsightGenieException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=401
        )


class AuthorizationError(InsightGenieException):
    """Raised when user is not authorized."""
    
    def __init__(self, message: str = "Not authorized"):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            status_code=403
        )


class ExternalAPIError(InsightGenieException):
    """Raised when external API call fails."""
    
    def __init__(
        self,
        message: str,
        api_name: str = "Unknown",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details["api_name"] = api_name
        super().__init__(
            message=message,
            code="EXTERNAL_API_ERROR",
            status_code=status_code,
            details=details
        )


class DatabaseError(InsightGenieException):
    """Raised when database operation fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            status_code=500,
            details=details
        )


class CacheError(InsightGenieException):
    """Raised when cache operation fails."""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="CACHE_ERROR",
            status_code=500
        )


class TaskExecutionError(InsightGenieException):
    """Raised when async task execution fails."""
    
    def __init__(
        self,
        message: str,
        task_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if task_name:
            details["task_name"] = task_name
        super().__init__(
            message=message,
            code="TASK_EXECUTION_ERROR",
            status_code=500,
            details=details
        )


class ConfigurationError(InsightGenieException):
    """Raised when configuration is invalid."""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        details = {"config_key": config_key} if config_key else {}
        super().__init__(
            message=message,
            code="CONFIGURATION_ERROR",
            status_code=500,
            details=details
        )


class TimeoutError(InsightGenieException):
    """Raised when operation times out."""
    
    def __init__(self, message: str = "Operation timed out"):
        super().__init__(
            message=message,
            code="TIMEOUT_ERROR",
            status_code=504
        )
