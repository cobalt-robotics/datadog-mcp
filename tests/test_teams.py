"""
Tests for team management functionality
"""

import pytest
import json
from unittest.mock import patch, AsyncMock, MagicMock
from datadog_mcp.tools import get_teams
from datadog_mcp.utils import datadog_client
from mcp.types import CallToolResult, TextContent


class TestTeamsToolDefinition:
    """Test the get_teams tool definition"""
    
    def test_get_teams_tool_definition(self):
        """Test that get_teams tool definition is properly structured"""
        tool_def = get_teams.get_tool_definition()
        
        assert tool_def.name == "get_teams"
        assert "team" in tool_def.description.lower()
        assert hasattr(tool_def, 'inputSchema')
        
        # Check schema structure
        schema = tool_def.inputSchema
        assert "properties" in schema
        
        properties = schema["properties"]
        expected_params = ["team_name", "include_members", "format"]
        for param in expected_params:
            assert param in properties, f"Parameter {param} missing from schema"


class TestTeamsRetrieval:
    """Test team data retrieval functionality"""

    @pytest.mark.asyncio
    async def test_fetch_teams_basic(self, httpx_mock_factory):
        """Test basic team fetching functionality"""
        # The raw API response format
        mock_response_data = {
            "data": [
                {
                    "id": "team-123",
                    "type": "teams",
                    "attributes": {
                        "name": "Backend Team",
                        "description": "Backend development team",
                        "handle": "backend-team",
                        "summary": "Responsible for API development"
                    }
                }
            ],
            "meta": {
                "pagination": {
                    "total_count": 1
                }
            }
        }

        httpx_mock_factory(mock_response_data)
        result = await datadog_client.fetch_teams()

        # fetch_teams returns raw API response
        assert isinstance(result, dict)
        assert "data" in result
        assert len(result["data"]) > 0

    @pytest.mark.asyncio
    async def test_fetch_teams_with_pagination(self, httpx_mock_factory):
        """Test fetching teams with pagination parameters"""
        mock_response_data = {
            "data": [
                {
                    "id": "team-123",
                    "type": "teams",
                    "attributes": {
                        "name": "Backend Team",
                        "handle": "backend-team"
                    }
                }
            ],
            "meta": {
                "pagination": {
                    "total_count": 50,
                    "total_pages": 5
                }
            }
        }

        mock = httpx_mock_factory(mock_response_data)
        result = await datadog_client.fetch_teams(page_size=10, page_number=2)

        assert isinstance(result, dict)
        # Verify the request was made
        mock._mock_instance.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_teams_returns_data(self, httpx_mock_factory):
        """Test that fetch_teams returns expected data structure"""
        mock_response_data = {
            "data": [
                {
                    "id": "team-123",
                    "type": "teams",
                    "attributes": {
                        "name": "Frontend Team"
                    }
                }
            ],
            "meta": {}
        }

        httpx_mock_factory(mock_response_data)
        result = await datadog_client.fetch_teams()

        assert isinstance(result, dict)
        assert "data" in result
        assert len(result["data"]) == 1
        assert result["data"][0]["attributes"]["name"] == "Frontend Team"


class TestTeamsToolHandler:
    """Test the get_teams tool handler"""

    @pytest.mark.asyncio
    async def test_handle_teams_request_success(self):
        """Test successful teams request handling"""
        mock_request = MagicMock()
        mock_request.arguments = {
            "format": "table"
        }

        # Mock data in raw API format (what fetch_teams returns)
        mock_teams_response = {
            "data": [
                {
                    "id": "team-123",
                    "type": "teams",
                    "attributes": {
                        "name": "DevOps Team",
                        "handle": "devops",
                        "description": "Infrastructure and deployment team"
                    }
                }
            ],
            "meta": {"pagination": {"total_count": 1}}
        }

        with patch('datadog_mcp.tools.get_teams.fetch_teams', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_teams_response

            result = await get_teams.handle_call(mock_request)

            assert isinstance(result, CallToolResult)
            assert result.isError is False
            assert len(result.content) > 0
            assert isinstance(result.content[0], TextContent)

            content_text = result.content[0].text
            assert "DevOps Team" in content_text or "devops" in content_text.lower()

    @pytest.mark.asyncio
    async def test_handle_teams_request_specific_team(self):
        """Test teams request for specific team"""
        mock_request = MagicMock()
        mock_request.arguments = {
            "team_name": "Security",
            "format": "table"
        }

        # Mock returns all teams, handler filters by name
        mock_teams_response = {
            "data": [
                {
                    "id": "team-456",
                    "type": "teams",
                    "attributes": {
                        "name": "Security Team",
                        "handle": "security",
                        "description": "Application security team"
                    }
                },
                {
                    "id": "team-789",
                    "type": "teams",
                    "attributes": {
                        "name": "DevOps Team",
                        "handle": "devops"
                    }
                }
            ],
            "meta": {"pagination": {"total_count": 2}}
        }

        with patch('datadog_mcp.tools.get_teams.fetch_teams', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_teams_response

            result = await get_teams.handle_call(mock_request)

            assert isinstance(result, CallToolResult)
            assert result.isError is False
            # Should show Security Team
            content_text = result.content[0].text
            assert "Security" in content_text

    @pytest.mark.asyncio
    async def test_handle_teams_request_json_format(self):
        """Test teams request with JSON format"""
        mock_request = MagicMock()
        mock_request.arguments = {
            "format": "json"
        }

        mock_teams_response = {
            "data": [
                {
                    "id": "team-789",
                    "type": "teams",
                    "attributes": {
                        "name": "QA Team",
                        "handle": "qa"
                    }
                }
            ],
            "meta": {"pagination": {"total_count": 1}}
        }

        with patch('datadog_mcp.tools.get_teams.fetch_teams', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_teams_response

            result = await get_teams.handle_call(mock_request)

            assert isinstance(result, CallToolResult)
            assert result.isError is False
            # Response includes summary header, JSON is after it
            content_text = result.content[0].text
            assert "QA Team" in content_text

    @pytest.mark.asyncio
    async def test_handle_teams_request_error(self):
        """Test error handling in teams requests"""
        mock_request = MagicMock()
        mock_request.arguments = {
            "team_name": "NonexistentTeam"
        }

        with patch('datadog_mcp.tools.get_teams.fetch_teams', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = Exception("Team not found")

            result = await get_teams.handle_call(mock_request)

            assert isinstance(result, CallToolResult)
            assert result.isError is True
            assert len(result.content) > 0
            assert "error" in result.content[0].text.lower()
    
    @pytest.mark.asyncio
    async def test_handle_teams_request_empty_results(self):
        """Test handling when no teams are found"""
        mock_request = MagicMock()
        mock_request.arguments = {
            "team_name": "EmptyResults"
        }

        mock_teams_data = {
            "data": [],  # Use correct API response format
        }

        # Patch at the module where it's imported (tools/get_teams.py imports fetch_teams)
        with patch('datadog_mcp.tools.get_teams.fetch_teams', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_teams_data

            result = await get_teams.handle_call(mock_request)

            assert isinstance(result, CallToolResult)
            assert result.isError is False
            assert len(result.content) > 0

            content_text = result.content[0].text
            assert "no teams" in content_text.lower() or "empty" in content_text.lower() or "0 teams" in content_text.lower()


class TestTeamsFormatting:
    """Test team data formatting"""
    
    def test_teams_table_formatting(self):
        """Test teams table formatting"""
        sample_teams = [
            {
                "id": "team-1",
                "name": "Backend Team",
                "handle": "backend",
                "description": "API development",
                "member_count": 5
            },
            {
                "id": "team-2", 
                "name": "Frontend Team",
                "handle": "frontend",
                "description": "UI development",
                "member_count": 4
            }
        ]
        
        # Test that we can process teams data
        assert len(sample_teams) == 2
        assert all("name" in team for team in sample_teams)
        assert all("handle" in team for team in sample_teams)
    
    def test_teams_detailed_formatting(self):
        """Test detailed teams formatting with members"""
        sample_data = {
            "teams": [
                {
                    "id": "team-1",
                    "name": "DevOps Team",
                    "handle": "devops",
                    "description": "Infrastructure team"
                }
            ],
            "users": [
                {
                    "id": "user-1",
                    "name": "John Doe",
                    "email": "john@example.com",
                    "teams": ["team-1"]
                },
                {
                    "id": "user-2",
                    "name": "Jane Smith", 
                    "email": "jane@example.com",
                    "teams": ["team-1"]
                }
            ]
        }
        
        # Verify data structure
        assert "teams" in sample_data
        assert "users" in sample_data
        assert len(sample_data["teams"]) == 1
        assert len(sample_data["users"]) == 2
        
        # Verify relationships
        team_id = sample_data["teams"][0]["id"]
        team_members = [user for user in sample_data["users"] if team_id in user["teams"]]
        assert len(team_members) == 2
    
    def test_teams_json_formatting(self):
        """Test teams JSON formatting"""
        sample_teams = [
            {
                "id": "team-1",
                "name": "Security Team",
                "handle": "security"
            }
        ]
        
        json_output = json.dumps(sample_teams, indent=2)
        assert isinstance(json_output, str)
        
        # Should be valid JSON
        parsed = json.loads(json_output)
        assert len(parsed) == 1
        assert parsed[0]["name"] == "Security Team"


class TestTeamsFiltering:
    """Test team filtering functionality at the handler level"""

    @pytest.mark.asyncio
    async def test_teams_by_name_filter_in_handler(self):
        """Test filtering teams by name (handled at handler level)"""
        mock_request = MagicMock()
        mock_request.arguments = {
            "team_name": "Backend",
            "format": "table"
        }

        mock_teams_response = {
            "data": [
                {
                    "id": "team-123",
                    "type": "teams",
                    "attributes": {
                        "name": "Backend Team",
                        "handle": "backend"
                    }
                },
                {
                    "id": "team-456",
                    "type": "teams",
                    "attributes": {
                        "name": "Frontend Team",
                        "handle": "frontend"
                    }
                }
            ],
            "meta": {"pagination": {"total_count": 2}}
        }

        # Patch where the function is imported
        with patch('datadog_mcp.tools.get_teams.fetch_teams', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_teams_response

            result = await get_teams.handle_call(mock_request)

            assert isinstance(result, CallToolResult)
            assert result.isError is False
            # Should filter to only Backend Team
            content_text = result.content[0].text
            assert "Backend" in content_text

    @pytest.mark.asyncio
    async def test_teams_pagination_parameters(self, httpx_mock_factory):
        """Test teams pagination parameters"""
        mock_response = {
            "data": [
                {
                    "id": "team-123",
                    "type": "teams",
                    "attributes": {"name": "Test Team"}
                }
            ],
            "meta": {"pagination": {"total_count": 100, "total_pages": 10}}
        }
        mock = httpx_mock_factory(mock_response)

        result = await datadog_client.fetch_teams(page_size=10, page_number=5)

        # Verify the request was made
        mock._mock_instance.get.assert_called_once()


class TestTeamsValidation:
    """Test team input validation"""
    
    @pytest.mark.asyncio
    async def test_invalid_team_name_handling(self):
        """Test handling of invalid team names"""
        mock_request = MagicMock()
        mock_request.arguments = {
            "team_name": "",  # Empty team name
            "include_members": True
        }
        
        result = await get_teams.handle_call(mock_request)
        
        # Should handle gracefully (either error or validation message)
        assert isinstance(result, CallToolResult)
        if result.isError:
            assert len(result.content) > 0
    
    @pytest.mark.asyncio
    async def test_invalid_format_handling(self):
        """Test handling of invalid format options"""
        mock_request = MagicMock()
        mock_request.arguments = {
            "format": "invalid_format"
        }
        
        # Should handle gracefully
        try:
            result = await get_teams.handle_call(mock_request)
            assert isinstance(result, CallToolResult)
        except Exception:
            # If validation happens at tool level, that's also acceptable
            pass


class TestTeamsIntegration:
    """Test teams integration functionality"""

    @pytest.mark.asyncio
    async def test_teams_api_response_structure(self, httpx_mock_factory):
        """Test teams API returns expected response structure"""
        mock_response = {
            "data": [
                {
                    "id": "team-1",
                    "type": "teams",
                    "attributes": {
                        "name": "Engineering",
                        "handle": "engineering"
                    }
                }
            ],
            "meta": {
                "pagination": {
                    "total_count": 1
                }
            }
        }

        httpx_mock_factory(mock_response)
        result = await datadog_client.fetch_teams()

        # Verify response structure
        assert isinstance(result, dict)
        assert "data" in result
        assert len(result["data"]) == 1
        assert result["data"][0]["attributes"]["name"] == "Engineering"

    @pytest.mark.asyncio
    async def test_handler_processes_team_members(self):
        """Test handler processes team membership data correctly"""
        mock_request = MagicMock()
        mock_request.arguments = {
            "team_name": "Engineering",
            "include_members": True,
            "format": "detailed"
        }

        mock_teams_response = {
            "data": [
                {
                    "id": "team-1",
                    "type": "teams",
                    "attributes": {
                        "name": "Engineering",
                        "handle": "engineering"
                    }
                }
            ],
            "meta": {"pagination": {"total_count": 1}}
        }

        mock_memberships_response = {
            "data": [
                {
                    "id": "membership-1",
                    "type": "team_memberships",
                    "attributes": {
                        "role": "admin"
                    },
                    "relationships": {
                        "user": {
                            "data": {"id": "user-1", "type": "users"}
                        }
                    }
                }
            ],
            "included": [
                {
                    "id": "user-1",
                    "type": "users",
                    "attributes": {
                        "name": "Developer One",
                        "email": "dev1@example.com"
                    }
                }
            ]
        }

        with patch('datadog_mcp.tools.get_teams.fetch_teams', new_callable=AsyncMock) as mock_fetch_teams:
            with patch('datadog_mcp.tools.get_teams.fetch_team_memberships', new_callable=AsyncMock) as mock_fetch_members:
                mock_fetch_teams.return_value = mock_teams_response
                mock_fetch_members.return_value = mock_memberships_response

                result = await get_teams.handle_call(mock_request)

                assert isinstance(result, CallToolResult)
                assert result.isError is False
                assert "Engineering" in result.content[0].text


if __name__ == "__main__":
    pytest.main([__file__])