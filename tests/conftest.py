"""
Pytest configuration and shared fixtures
"""

import pytest
import os
from unittest.mock import patch, MagicMock, AsyncMock


@pytest.fixture
def mock_env_credentials():
    """Mock environment with valid Datadog credentials"""
    with patch.dict(os.environ, {"DD_API_KEY": "test_key", "DD_APP_KEY": "test_app", "DD_COOKIE": ""}):
        # Also patch the module-level variables that were set at import time
        from datadog_mcp.utils import datadog_client
        with patch.object(datadog_client, 'DATADOG_API_KEY', "test_key"):
            with patch.object(datadog_client, 'DATADOG_APP_KEY', "test_app"):
                with patch.object(datadog_client, 'get_cookie', return_value=None):
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