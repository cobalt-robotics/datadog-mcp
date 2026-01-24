"""
Test for correct query syntax with as_count and aggregation_by
This test verifies the fix for query ordering: aggregation_by must come before .as_count()
"""

import pytest
from datadog_mcp.utils import datadog_client


class TestQuerySyntaxFix:
    """Test that query syntax is correct for as_count with aggregation_by"""

    @pytest.mark.asyncio
    async def test_query_syntax_with_aggregation_and_as_count(self, httpx_mock_factory):
        """
        Test that the query is constructed with correct syntax:
        sum:metric{*} by {field}.as_count()
        NOT: sum:metric{*}.as_count() by {field} (this is invalid)
        """
        mock_response = {
            "status": "ok",
            "series": [{
                "metric": "test.metric",
                "tag_set": ["variant:N/A"],
                "pointlist": [[1640995200000, 1.0]]
            }]
        }

        mock = httpx_mock_factory(mock_response)

        # Call fetch_metrics with both aggregation_by and as_count
        await datadog_client.fetch_metrics(
            metric_name="test.metric",
            aggregation_by=["variant"],
            as_count=True
        )

        # Verify the query was constructed correctly
        call_args = mock._mock_instance.get.call_args
        params = call_args[1]["params"]
        query = params["query"]

        # The correct syntax should be: avg:test.metric{*} by {variant}.as_count()
        # (avg is the default aggregation)
        assert query == "avg:test.metric{*} by {variant}.as_count()", \
            f"Query syntax is incorrect. Got: {query}"

        # Verify that .as_count() comes AFTER the by clause
        by_index = query.find(" by {")
        as_count_index = query.find(".as_count()")

        assert by_index < as_count_index, \
            "The 'by' clause must come before .as_count() in the query"

    @pytest.mark.asyncio
    async def test_query_syntax_with_multiple_aggregation_fields(self, httpx_mock_factory):
        """Test query syntax with multiple aggregation fields and as_count"""
        mock_response = {"status": "ok", "series": []}

        mock = httpx_mock_factory(mock_response)

        # Call with multiple aggregation fields
        await datadog_client.fetch_metrics(
            metric_name="test.metric",
            aggregation_by=["variant", "status"],
            as_count=True
        )

        call_args = mock._mock_instance.get.call_args
        params = call_args[1]["params"]
        query = params["query"]

        # Should be: avg:test.metric{*} by {variant,status}.as_count()
        assert query == "avg:test.metric{*} by {variant,status}.as_count()", \
            f"Query syntax is incorrect. Got: {query}"

    @pytest.mark.asyncio
    async def test_query_syntax_with_filters_and_aggregation_as_count(self, httpx_mock_factory):
        """Test query syntax with filters, aggregation_by, and as_count"""
        mock_response = {"status": "ok", "series": []}

        mock = httpx_mock_factory(mock_response)

        # Call with filters, aggregation, and as_count
        await datadog_client.fetch_metrics(
            metric_name="test.metric",
            filters={"env": "prod"},
            aggregation_by=["service"],
            as_count=True
        )

        call_args = mock._mock_instance.get.call_args
        params = call_args[1]["params"]
        query = params["query"]

        # Should be: avg:test.metric{env:prod} by {service}.as_count()
        assert query == "avg:test.metric{env:prod} by {service}.as_count()", \
            f"Query syntax is incorrect. Got: {query}"

    @pytest.mark.asyncio
    async def test_query_syntax_as_count_without_aggregation(self, httpx_mock_factory):
        """Test that as_count without aggregation_by still works"""
        mock_response = {"status": "ok", "series": []}

        mock = httpx_mock_factory(mock_response)

        # Call with as_count but no aggregation_by
        await datadog_client.fetch_metrics(
            metric_name="test.metric",
            as_count=True
        )

        call_args = mock._mock_instance.get.call_args
        params = call_args[1]["params"]
        query = params["query"]

        # Should be: avg:test.metric{*}.as_count()
        assert query == "avg:test.metric{*}.as_count()", \
            f"Query syntax is incorrect. Got: {query}"
