"""
Tests for authentication mechanisms (API keys and cookies)
"""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock


class TestCookieLoading:
    """Tests for cookie loading functionality"""

    def test_get_cookie_from_env(self):
        """Test loading cookie from DD_COOKIE environment variable"""
        with patch.dict(os.environ, {"DD_COOKIE": "test_cookie_value"}, clear=False):
            # Need to reimport to pick up the patched env
            from datadog_mcp.utils import datadog_client
            # Reload the function to use fresh env
            result = datadog_client.get_cookie()
            assert result == "test_cookie_value"

    def test_get_cookie_from_file(self):
        """Test loading cookie from file when env var not set"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cookie', delete=False) as f:
            f.write("file_cookie_value")
            cookie_file = f.name

        try:
            with patch.dict(os.environ, {"DD_COOKIE": "", "DD_COOKIE_FILE": cookie_file}, clear=False):
                from datadog_mcp.utils import datadog_client
                # Patch the COOKIE_FILE_PATH to use our temp file
                with patch.object(datadog_client, 'COOKIE_FILE_PATH', cookie_file):
                    result = datadog_client.get_cookie()
                    assert result == "file_cookie_value"
        finally:
            os.unlink(cookie_file)

    def test_get_cookie_returns_none_when_not_set(self):
        """Test that get_cookie returns None when no cookie is configured"""
        with tempfile.TemporaryDirectory() as tmpdir:
            nonexistent_file = os.path.join(tmpdir, "nonexistent")
            with patch.dict(os.environ, {"DD_COOKIE": ""}, clear=False):
                from datadog_mcp.utils import datadog_client
                with patch.object(datadog_client, 'COOKIE_FILE_PATH', nonexistent_file):
                    result = datadog_client.get_cookie()
                    assert result is None

    def test_save_cookie(self):
        """Test saving cookie to file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cookie_file = os.path.join(tmpdir, "test_cookie")

            from datadog_mcp.utils import datadog_client
            with patch.object(datadog_client, 'COOKIE_FILE_PATH', cookie_file):
                path = datadog_client.save_cookie("saved_cookie_value")

                assert path == cookie_file
                assert os.path.exists(cookie_file)

                with open(cookie_file) as f:
                    assert f.read() == "saved_cookie_value"

                # Check permissions are restricted
                stat_result = os.stat(cookie_file)
                assert stat_result.st_mode & 0o777 == 0o600

    def test_save_cookie_strips_whitespace(self):
        """Test that save_cookie strips whitespace from cookie value"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cookie_file = os.path.join(tmpdir, "test_cookie")

            from datadog_mcp.utils import datadog_client
            with patch.object(datadog_client, 'COOKIE_FILE_PATH', cookie_file):
                datadog_client.save_cookie("  cookie_with_whitespace  \n")

                with open(cookie_file) as f:
                    assert f.read() == "cookie_with_whitespace"


class TestAuthHeaders:
    """Tests for get_auth_headers function"""

    def test_auth_headers_with_cookie(self):
        """Test that cookie auth headers are returned when cookie is available"""
        from datadog_mcp.utils import datadog_client

        with patch.object(datadog_client, 'get_cookie', return_value="test_cookie"):
            headers = datadog_client.get_auth_headers()

            assert headers["Content-Type"] == "application/json"
            assert headers["Cookie"] == "test_cookie"
            assert "DD-API-KEY" not in headers

    def test_auth_headers_with_api_keys(self):
        """Test that API key headers are returned when no cookie but keys are set"""
        from datadog_mcp.utils import datadog_client

        with patch.object(datadog_client, 'get_cookie', return_value=None):
            with patch.object(datadog_client, 'DATADOG_API_KEY', "test_api_key"):
                with patch.object(datadog_client, 'DATADOG_APP_KEY', "test_app_key"):
                    headers = datadog_client.get_auth_headers()

                    assert headers["Content-Type"] == "application/json"
                    assert headers["DD-API-KEY"] == "test_api_key"
                    assert headers["DD-APPLICATION-KEY"] == "test_app_key"
                    assert "Cookie" not in headers

    def test_auth_headers_cookie_takes_priority(self):
        """Test that cookie auth takes priority over API keys"""
        from datadog_mcp.utils import datadog_client

        with patch.object(datadog_client, 'get_cookie', return_value="priority_cookie"):
            with patch.object(datadog_client, 'DATADOG_API_KEY', "test_api_key"):
                with patch.object(datadog_client, 'DATADOG_APP_KEY', "test_app_key"):
                    headers = datadog_client.get_auth_headers()

                    assert headers["Cookie"] == "priority_cookie"
                    assert "DD-API-KEY" not in headers

    def test_auth_headers_raises_when_no_credentials(self):
        """Test that ValueError is raised when no credentials are available"""
        from datadog_mcp.utils import datadog_client

        with patch.object(datadog_client, 'get_cookie', return_value=None):
            with patch.object(datadog_client, 'DATADOG_API_KEY', None):
                with patch.object(datadog_client, 'DATADOG_APP_KEY', None):
                    with pytest.raises(ValueError, match="No Datadog credentials available"):
                        datadog_client.get_auth_headers()


class TestAuthMode:
    """Tests for get_auth_mode and get_api_url functions"""

    def test_auth_mode_with_cookie(self):
        """Test that cookie auth mode returns app.datadoghq.com"""
        from datadog_mcp.utils import datadog_client

        with patch.object(datadog_client, 'get_cookie', return_value="some_cookie"):
            use_cookie, url = datadog_client.get_auth_mode()

            assert use_cookie is True
            assert url == "https://app.datadoghq.com"

    def test_auth_mode_without_cookie(self):
        """Test that API key auth mode returns api.datadoghq.com"""
        from datadog_mcp.utils import datadog_client

        with patch.object(datadog_client, 'get_cookie', return_value=None):
            use_cookie, url = datadog_client.get_auth_mode()

            assert use_cookie is False
            assert url == "https://api.datadoghq.com"

    def test_get_api_url_dynamic(self):
        """Test that get_api_url returns correct URL based on auth mode"""
        from datadog_mcp.utils import datadog_client

        # With cookie
        with patch.object(datadog_client, 'get_cookie', return_value="cookie"):
            assert datadog_client.get_api_url() == "https://app.datadoghq.com"

        # Without cookie
        with patch.object(datadog_client, 'get_cookie', return_value=None):
            assert datadog_client.get_api_url() == "https://api.datadoghq.com"


class TestDynamicCookieUpdate:
    """Tests to verify cookies can be updated without restart"""

    def test_cookie_change_reflected_immediately(self):
        """Test that changing cookie file is reflected in next get_auth_headers call"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cookie_file = os.path.join(tmpdir, "dynamic_cookie")

            from datadog_mcp.utils import datadog_client

            with patch.dict(os.environ, {"DD_COOKIE": ""}, clear=False):
                with patch.object(datadog_client, 'COOKIE_FILE_PATH', cookie_file):
                    with patch.object(datadog_client, 'DATADOG_API_KEY', "fallback_key"):
                        with patch.object(datadog_client, 'DATADOG_APP_KEY', "fallback_app"):
                            # Initially no cookie file - should use API keys
                            headers1 = datadog_client.get_auth_headers()
                            assert "DD-API-KEY" in headers1

                            # Create cookie file
                            with open(cookie_file, 'w') as f:
                                f.write("new_cookie_value")

                            # Now should use cookie
                            headers2 = datadog_client.get_auth_headers()
                            assert headers2["Cookie"] == "new_cookie_value"
                            assert "DD-API-KEY" not in headers2

                            # Update cookie file
                            with open(cookie_file, 'w') as f:
                                f.write("updated_cookie_value")

                            # Should reflect update
                            headers3 = datadog_client.get_auth_headers()
                            assert headers3["Cookie"] == "updated_cookie_value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
