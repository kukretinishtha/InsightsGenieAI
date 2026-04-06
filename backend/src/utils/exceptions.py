"""Exception classes for InsightGenie AI."""

from typing import Any, Dict, Optional


class InsightGenieException(Exception):
    """Base exception for InsightGenie AI."""

    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize exception.

        Args:
            message: Error message
            error_code: Error code identifier
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class AgentExecutionError(InsightGenieException):
    """Exception raised during agent execution."""

    def __init__(self, message: str, agent_id: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            error_code="AGENT_EXECUTION_ERROR",
            details={"agent_id": agent_id, **kwargs}
        )


class ToolExecutionError(InsightGenieException):
    """Exception raised during tool execution."""

    def __init__(self, message: str, tool_name: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            error_code="TOOL_EXECUTION_ERROR",
            details={"tool_name": tool_name, **kwargs}
        )


class GenieAPIError(InsightGenieException):
    """Exception raised when calling Genie API."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code="GENIE_API_ERROR",
            details=kwargs
        )


class DataSourceError(InsightGenieException):
    """Exception raised when accessing data sources."""

    def __init__(self, message: str, source: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            error_code="DATA_SOURCE_ERROR",
            details={"source": source, **kwargs}
        )


class ValidationError(InsightGenieException):
    """Exception raised during validation."""

    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            error_code="VALIDATION_ERROR",
            details={"field": field, **kwargs}
        )


class TimeoutError(InsightGenieException):
    """Exception raised on operation timeout."""

    def __init__(self, message: str, timeout_seconds: Optional[int] = None, **kwargs):
        super().__init__(
            message,
            error_code="TIMEOUT_ERROR",
            details={"timeout_seconds": timeout_seconds, **kwargs}
        )
