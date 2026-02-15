"""Tests for finnhub MCP server functionality."""

import pytest
import json
import os
from unittest.mock import patch, MagicMock
from fastmcp import Client


class TestSkillResource:
    """Test the skill resource and server instructions."""

    @pytest.mark.asyncio
    async def test_initialize_returns_instructions(self, mcp_server):
        """Server instructions reference the skill resource."""
        async with Client(mcp_server) as client:
            result = await client.initialize()
            assert result.instructions is not None
            assert "skill://finnhub/usage" in result.instructions

    @pytest.mark.asyncio
    async def test_skill_resource_listed(self, mcp_server):
        """skill://finnhub/usage appears in resource listing."""
        async with Client(mcp_server) as client:
            resources = await client.list_resources()
            uris = [str(r.uri) for r in resources]
            assert "skill://finnhub/usage" in uris

    @pytest.mark.asyncio
    async def test_skill_resource_readable(self, mcp_server):
        """Reading the skill resource returns the full skill content."""
        async with Client(mcp_server) as client:
            contents = await client.read_resource("skill://finnhub/usage")
            text = contents[0].text if hasattr(contents[0], "text") else str(contents[0])
            assert "Tool Selection" in text
            assert "get_stock_quote" in text
            assert "get_basic_financials" in text


@pytest.mark.asyncio
async def test_tools_list(mcp_server):
    """Test that tools are properly registered"""
    async with Client(mcp_server) as client:
        tools = await client.list_tools()
        
        assert len(tools) == 5
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "get_market_news", 
            "get_stock_quote", 
            "get_company_profile", 
            "get_basic_financials", 
            "get_recommendation_trends"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
            
        # Check tool descriptions
        market_news_tool = next(t for t in tools if t.name == "get_market_news")
        assert "Get latest market news from Finnhub" in market_news_tool.description
        
        stock_quote_tool = next(t for t in tools if t.name == "get_stock_quote")
        assert "Get current stock quote for a symbol" in stock_quote_tool.description


@pytest.mark.asyncio
async def test_stock_quote_missing_symbol(mcp_server):
    """Test calling stock quote without required symbol parameter."""
    async with Client(mcp_server) as client:
        try:
            await client.call_tool("get_stock_quote", {})
            assert False, "Should have raised an exception"
        except Exception as e:
            # Should raise an exception for missing required parameter
            assert "symbol" in str(e).lower() or "required" in str(e).lower()


@pytest.mark.asyncio
async def test_invalid_tool(mcp_server):
    """Test calling invalid tool"""
    async with Client(mcp_server) as client:
        try:
            await client.call_tool("invalid_tool", {})
            assert False, "Should have raised an exception"
        except Exception as e:
            # Should raise an exception for invalid tool
            assert "invalid_tool" in str(e).lower() or "not found" in str(e).lower()


@patch.dict(os.environ, {"FINNHUB_API_KEY": "test_api_key"})
@patch("finnhub.Client")
@pytest.mark.asyncio
async def test_get_stock_quote_with_mock(mock_finnhub_client, mcp_server):
    """Test get_stock_quote tool with mocked Finnhub API"""
    # Mock the Finnhub client response
    mock_client = MagicMock()
    mock_finnhub_client.return_value = mock_client
    mock_client.quote.return_value = {
        "c": 150.0,  # current price
        "d": 2.5,    # change
        "dp": 1.69,  # percent change
        "h": 152.0,  # high
        "l": 148.0,  # low
        "o": 149.0,  # open
        "pc": 147.5, # previous close
        "t": 1640995200  # timestamp
    }
    
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_stock_quote", {"symbol": "AAPL"})
        
        # Parse the JSON result
        result_data = json.loads(result.data)
        assert result_data["symbol"] == "AAPL"
        assert result_data["current_price"] == 150.0
        assert result_data["change"] == 2.5
        assert result_data["percent_change"] == 1.69
        assert "retrieved_at" in result_data


@patch.dict(os.environ, {"FINNHUB_API_KEY": "test_api_key"})
@patch("finnhub.Client")
@pytest.mark.asyncio
async def test_get_market_news_with_mock(mock_finnhub_client, mcp_server):
    """Test get_market_news tool with mocked Finnhub API"""
    # Mock the Finnhub client response
    mock_client = MagicMock()
    mock_finnhub_client.return_value = mock_client
    mock_client.general_news.return_value = [
        {
            "headline": "Test Market News",
            "summary": "Test summary",
            "url": "https://example.com",
            "datetime": 1640995200,
            "source": "Test Source",
            "category": "general"
        }
    ]
    
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_market_news", {"category": "general"})
        
        # Parse the JSON result
        result_data = json.loads(result.data)
        assert result_data["category"] == "general"
        assert result_data["count"] == 1
        assert len(result_data["news"]) == 1
        assert result_data["news"][0]["headline"] == "Test Market News"
        assert "timestamp" in result_data


@pytest.mark.asyncio
async def test_get_stock_quote_no_api_key(mcp_server):
    """Test get_stock_quote tool without API key"""
    # Ensure no API key is set
    with patch.dict(os.environ, {}, clear=True):
        async with Client(mcp_server) as client:
            result = await client.call_tool("get_stock_quote", {"symbol": "AAPL"})
            
            # Parse the JSON result - should contain error
            result_data = json.loads(result.data)
            assert "error" in result_data
            assert "FINNHUB_API_KEY" in result_data["error"]