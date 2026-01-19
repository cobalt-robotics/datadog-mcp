"""
Integration tests that verify the overall system works without requiring real API calls
"""

import importlib
import os

import pytest
from unittest.mock import patch, MagicMock

from datadog_mcp.server import TOOLS, handle_list_tools, handle_call_tool
from datadog_mcp.utils import datadog_client
from mcp.types import Tool, TextContent


class TestBasicIntegration:
    """Test basic integration without external dependencies"""
    
    def test_all_tools_are_registered(self):
        """Test that all expected tools are in the registry"""
        expected_tools = [
            "list_ci_pipelines",
            "get_pipeline_fingerprints",
            "get_logs", 
            "get_teams",
            "get_metrics",
            "get_metric_fields",
            "get_metric_field_values",
            "list_metrics",
            "list_service_definitions",
            "get_service_definition"
        ]
        
        for tool_name in expected_tools:
            assert tool_name in TOOLS, f"Tool {tool_name} not registered"
            assert "definition" in TOOLS[tool_name]
            assert "handler" in TOOLS[tool_name]
    
    @pytest.mark.asyncio
    async def test_list_tools_returns_valid_definitions(self):
        """Test that list_tools returns valid Tool objects"""
        tools = await handle_list_tools()
        
        assert isinstance(tools, list)
        assert len(tools) == len(TOOLS)
        
        for tool in tools:
            assert isinstance(tool, Tool)
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            assert hasattr(tool, 'inputSchema')
    
    @pytest.mark.asyncio
    async def test_tool_definitions_are_valid(self):
        """Test that each tool definition is properly structured"""
        for tool_name, tool_config in TOOLS.items():
            tool_def = tool_config["definition"]()
            
            assert isinstance(tool_def, Tool)
            assert tool_def.name == tool_name
            assert len(tool_def.description) > 0
            assert isinstance(tool_def.inputSchema, dict)
            assert "properties" in tool_def.inputSchema


class TestToolHandling:
    """Test tool call handling"""
    
    @pytest.mark.asyncio
    async def test_handle_unknown_tool(self):
        """Test handling of unknown tools"""
        result = await handle_call_tool("unknown_tool", {})
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Unknown tool" in result[0].text
    
    @pytest.mark.asyncio
    async def test_handle_tool_with_empty_arguments(self):
        """Test handling tools with empty arguments"""
        # Pick any tool and try with empty args
        tool_name = "list_ci_pipelines"
        
        with patch.dict(os.environ, {"DD_API_KEY": "test", "DD_APP_KEY": "test"}):
            with patch('datadog_mcp.utils.datadog_client.httpx.AsyncClient') as mock_client:
                # Mock successful response
                mock_response = MagicMock()
                mock_response.json.return_value = {"data": []}
                mock_response.raise_for_status.return_value = None
                mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
                
                result = await handle_call_tool(tool_name, {})
                
                assert isinstance(result, list)
                assert len(result) >= 1
                assert isinstance(result[0], TextContent)


class TestEnvironmentHandling:
    """Test environment configuration handling"""
    
    def test_missing_credentials_handling(self):
        """Test that missing credentials don't crash - just log warning"""
        # Clear environment - module should load without raising
        with patch.dict(os.environ, {}, clear=True):
            # Should not raise - just logs a warning
            importlib.reload(datadog_client)
            # Verify module loaded successfully
            assert hasattr(datadog_client, 'get_auth_headers')
    
    def test_valid_credentials_accepted(self):
        """Test that valid credentials work"""
        with patch.dict(os.environ, {"DD_API_KEY": "test_key", "DD_APP_KEY": "test_app"}):
            # Should not raise
            import importlib
            from datadog_mcp.utils import datadog_client
            importlib.reload(datadog_client)
            
            assert datadog_client.DATADOG_API_KEY == "test_key"
            assert datadog_client.DATADOG_APP_KEY == "test_app"


class TestToolParameters:
    """Test tool parameter validation"""
    
    def test_tool_schemas_have_required_structure(self):
        """Test that all tools have proper schema structure"""
        for tool_name, tool_config in TOOLS.items():
            tool_def = tool_config["definition"]()
            schema = tool_def.inputSchema
            
            # Basic schema validation
            assert isinstance(schema, dict)
            assert "type" in schema
            assert schema["type"] == "object"
            
            if "properties" in schema:
                assert isinstance(schema["properties"], dict)
            
            if "required" in schema:
                assert isinstance(schema["required"], list)
    
    def test_common_parameters_exist(self):
        """Test that common parameters exist where expected"""
        # Tools that should have format parameter
        format_tools = ["get_logs", "get_teams", "get_metrics", "list_metrics"]
        
        for tool_name in format_tools:
            if tool_name in TOOLS:
                tool_def = TOOLS[tool_name]["definition"]()
                properties = tool_def.inputSchema.get("properties", {})
                assert "format" in properties, f"Tool {tool_name} missing format parameter"


class TestErrorHandling:
    """Test error handling across the system"""
    
    @pytest.mark.asyncio
    async def test_tool_exception_handling(self):
        """Test that tool exceptions are properly handled"""
        # Create a mock tool that raises an exception
        def failing_handler(request):
            raise Exception("Test error")
        
        original_tools = TOOLS.copy()
        TOOLS["test_failing_tool"] = {
            "definition": lambda: Tool(name="test_failing_tool", description="Test", inputSchema={}),
            "handler": failing_handler
        }
        
        try:
            result = await handle_call_tool("test_failing_tool", {})
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Error" in result[0].text
            
        finally:
            # Restore original tools
            TOOLS.clear()
            TOOLS.update(original_tools)


class TestModuleStructure:
    """Test the overall module structure"""
    
    def test_all_required_modules_importable(self):
        """Test that all required modules can be imported"""
        # Test core modules
        from datadog_mcp import server
        from datadog_mcp.utils import datadog_client, formatters
        
        # Test tool modules
        from datadog_mcp.tools import (
            get_logs, get_teams, get_metrics,
            list_metrics, get_metric_fields, get_metric_field_values,
            list_pipelines, get_fingerprints,
            list_service_definitions, get_service_definition
        )
        
        # All imports should succeed
        assert server is not None
        assert datadog_client is not None
        assert formatters is not None
    
    def test_tool_modules_have_required_functions(self):
        """Test that tool modules have required functions"""
        tool_modules = [
            "get_logs", "get_teams", "get_metrics", "list_metrics",
            "get_metric_fields", "get_metric_field_values",
            "list_pipelines", "get_fingerprints", 
            "list_service_definitions", "get_service_definition"
        ]
        
        for module_name in tool_modules:
            module = __import__(f"datadog_mcp.tools.{module_name}", fromlist=[module_name])
            
            # Each tool module should have these functions
            assert hasattr(module, "get_tool_definition"), f"{module_name} missing get_tool_definition"
            assert hasattr(module, "handle_call"), f"{module_name} missing handle_call"
            assert callable(getattr(module, "get_tool_definition"))
            assert callable(getattr(module, "handle_call"))


if __name__ == "__main__":
    pytest.main([__file__])