"""Unit tests for custom exceptions."""

import pytest
from app.utils.exceptions import (
    ValidationError,
    NotFoundError,
    AuthenticationError,
    ExternalAPIError,
    TaskExecutionError,
    ConfigurationError
)


def test_validation_error():
    """Test validation error."""
    error = ValidationError("Invalid input", details={"field": "email"})
    
    assert error.status_code == 400
    assert error.code == "VALIDATION_ERROR"
    assert error.details["field"] == "email"


def test_not_found_error():
    """Test not found error."""
    error = NotFoundError("User not found", resource="User")
    
    assert error.status_code == 404
    assert error.code == "NOT_FOUND"
    assert error.details["resource"] == "User"


def test_authentication_error():
    """Test authentication error."""
    error = AuthenticationError("Invalid credentials")
    
    assert error.status_code == 401
    assert error.code == "AUTHENTICATION_ERROR"


def test_external_api_error():
    """Test external API error."""
    error = ExternalAPIError(
        "API request failed",
        api_name="GenieAPI",
        status_code=500
    )
    
    assert error.status_code == 500
    assert error.code == "EXTERNAL_API_ERROR"
    assert error.details["api_name"] == "GenieAPI"


def test_task_execution_error():
    """Test task execution error."""
    error = TaskExecutionError(
        "Task failed",
        task_name="analyze_stock"
    )
    
    assert error.status_code == 500
    assert error.code == "TASK_EXECUTION_ERROR"
    assert error.details["task_name"] == "analyze_stock"


def test_configuration_error():
    """Test configuration error."""
    error = ConfigurationError(
        "Invalid config",
        config_key="DATABASE_URL"
    )
    
    assert error.status_code == 500
    assert error.code == "CONFIGURATION_ERROR"
    assert error.details["config_key"] == "DATABASE_URL"
