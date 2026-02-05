"""
Pytest configuration and shared fixtures
"""

import pytest
import os
from unittest.mock import patch, MagicMock, AsyncMock


@pytest.fixture
def mock_env_credentials():
    """Mock environment with valid Datadog credentials (via AWS Secrets Manager mock)"""
    from datadog_mcp.utils import datadog_client
    from datadog_mcp.utils.secrets_provider import DatadogCredentials
    from datetime import datetime, timezone, timedelta

    mock_creds = DatadogCredentials(
        api_key="test_key",
        app_key="test_app",
        fetched_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    mock_provider = AsyncMock()
    mock_provider.get_credentials.return_value = mock_creds

    with patch.dict(os.environ, {"DD_COOKIE": ""}, clear=False):
        with patch.object(datadog_client, 'get_cookie', return_value=None):
            with patch.object(datadog_client, 'get_secret_provider', return_value=mock_provider):
                yield


@pytest.fixture
def mock_auth_headers():
    """
    Mock get_auth_headers to return test credentials.
    Use this for tests that call API functions directly.
    """
    from datadog_mcp.utils import datadog_client

    async def mock_get_auth_headers(include_csrf=False):
        return {
            "Content-Type": "application/json",
            "DD-API-KEY": "test_key",
            "DD-APPLICATION-KEY": "test_app",
        }

    with patch.object(datadog_client, 'get_auth_headers', mock_get_auth_headers):
        yield


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client for API calls"""
    with patch('datadog_mcp.utils.datadog_client.httpx.AsyncClient') as mock_client:
        # Setup default successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}
        mock_response.raise_for_status.return_value = None

        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

        yield mock_client


def create_httpx_mock(response_data):
    """
    Create a properly configured httpx.AsyncClient mock for async context manager usage.

    This handles the async context manager protocol and async get/post methods correctly.

    Usage:
        with create_httpx_mock({"data": []}) as mock_client:
            result = await some_function_using_httpx()
    """
    mock_client = patch('datadog_mcp.utils.datadog_client.httpx.AsyncClient')
    mock = mock_client.start()

    # Create mock response object (httpx response methods are sync)
    mock_response = MagicMock()
    mock_response.json.return_value = response_data
    mock_response.raise_for_status.return_value = None
    mock_response.status_code = 200
    mock_response.text = str(response_data)

    # Create mock client instance with async get/post methods
    mock_instance = MagicMock()
    mock_instance.get = AsyncMock(return_value=mock_response)
    mock_instance.post = AsyncMock(return_value=mock_response)

    # Configure async context manager
    mock.__aenter__ = AsyncMock(return_value=mock_instance)
    mock.__aexit__ = AsyncMock(return_value=None)
    mock.return_value.__aenter__ = AsyncMock(return_value=mock_instance)
    mock.return_value.__aexit__ = AsyncMock(return_value=None)

    # Attach mock objects for test assertions
    mock._mock_response = mock_response
    mock._mock_instance = mock_instance
    mock._patch = mock_client

    # Also mock get_auth_headers to return test credentials
    from datadog_mcp.utils import datadog_client

    async def mock_get_auth_headers(include_csrf=False):
        return {
            "Content-Type": "application/json",
            "DD-API-KEY": "test_key",
            "DD-APPLICATION-KEY": "test_app",
        }

    auth_patch = patch.object(datadog_client, 'get_auth_headers', mock_get_auth_headers)
    auth_patch.start()
    mock._auth_patch = auth_patch

    return mock


@pytest.fixture
def httpx_mock_factory():
    """
    Factory fixture for creating httpx mocks with custom response data.

    Usage:
        def test_something(httpx_mock_factory):
            mock = httpx_mock_factory({"data": [{"id": "1"}]})
            result = await some_api_call()
            mock._patch.stop()  # Clean up
    """
    mocks = []

    def _create(response_data):
        mock = create_httpx_mock(response_data)
        mocks.append(mock)
        return mock

    yield _create

    # Clean up all mocks
    for mock in mocks:
        mock._patch.stop()
        if hasattr(mock, '_auth_patch'):
            mock._auth_patch.stop()


@pytest.fixture
def sample_request():
    """Create a sample request object"""
    request = MagicMock()
    request.arguments = {}
    return request


@pytest.fixture
def sample_logs_data():
    """Sample logs data for testing - returns dict with data and meta keys"""
    return {
        "data": [
            {
                "id": "log-1",
                "attributes": {
                    "timestamp": "2023-01-01T12:00:00Z",
                    "message": "Test log message",
                    "service": "test-service",
                    "status": "info",
                    "host": "test-host"
                }
            },
            {
                "id": "log-2",
                "attributes": {
                    "timestamp": "2023-01-01T12:01:00Z",
                    "message": "Error occurred",
                    "service": "test-service",
                    "status": "error",
                    "host": "test-host"
                }
            }
        ],
        "meta": {
            "page": {
                "after": None
            }
        }
    }


@pytest.fixture
def sample_logs_data_with_numeric_timestamp():
    """Sample logs data with numeric timestamps (regression test for int subscript bug)"""
    return {
        "data": [
            {
                "id": "log-1",
                "attributes": {
                    "timestamp": 1737745200,  # Unix timestamp as integer
                    "message": "Test log with numeric timestamp",
                    "service": "test-service",
                    "status": "error",
                    "host": "test-host"
                }
            },
            {
                "id": "log-2",
                "attributes": {
                    "timestamp": None,  # None timestamp
                    "message": "Test log with None timestamp",
                    "service": None,  # None service
                    "status": 500,  # Numeric status code
                    "host": None
                }
            }
        ],
        "meta": {
            "page": {
                "after": None
            }
        }
    }


@pytest.fixture
def sample_metrics_data():
    """Sample metrics data for testing"""
    return {
        "data": {
            "attributes": {
                "series": [
                    {
                        "metric": "system.cpu.user",
                        "points": [
                            [1640995200000, 25.5],
                            [1640995260000, 30.2]
                        ],
                        "tags": ["host:web-01", "env:prod"]
                    }
                ]
            }
        }
    }


@pytest.fixture
def sample_teams_data():
    """Sample teams data for testing"""
    return {
        "teams": [
            {
                "id": "team-123",
                "name": "Backend Team",
                "handle": "backend-team",
                "description": "Backend development team"
            }
        ],
        "users": [
            {
                "id": "user-1",
                "name": "John Doe",
                "email": "john@example.com",
                "teams": ["team-123"]
            }
        ]
    }