"""Tests for finnhub MCP server functionality."""

import json
import os
from unittest.mock import MagicMock, patch

import pytest
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

        assert len(tools) == 10
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "get_market_news",
            "get_stock_quote",
            "get_company_profile",
            "get_basic_financials",
            "get_recommendation_trends",
            "get_insider_transactions",
            "get_insider_sentiment",
            "get_earnings_calendar",
            "get_peers",
            "get_company_news",
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
            raise AssertionError("Should have raised an exception")
        except Exception as e:
            # Should raise an exception for missing required parameter
            assert "symbol" in str(e).lower() or "required" in str(e).lower()


@pytest.mark.asyncio
async def test_invalid_tool(mcp_server):
    """Test calling invalid tool"""
    async with Client(mcp_server) as client:
        try:
            await client.call_tool("invalid_tool", {})
            raise AssertionError("Should have raised an exception")
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
        "d": 2.5,  # change
        "dp": 1.69,  # percent change
        "h": 152.0,  # high
        "l": 148.0,  # low
        "o": 149.0,  # open
        "pc": 147.5,  # previous close
        "t": 1640995200,  # timestamp
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
            "category": "general",
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


# --- Tests for new tools ---


@patch.dict(os.environ, {"FINNHUB_API_KEY": "test_api_key"})
@patch("finnhub.Client")
@pytest.mark.asyncio
async def test_get_insider_transactions_with_mock(mock_finnhub_client, mcp_server):
    """Test get_insider_transactions returns formatted insider trades."""
    mock_client = MagicMock()
    mock_finnhub_client.return_value = mock_client
    mock_client.stock_insider_transactions.return_value = {
        "data": [
            {
                "name": "John Doe",
                "share": 50000,
                "change": 10000,
                "filingDate": "2026-03-15",
                "transactionDate": "2026-03-12",
                "transactionCode": "P",
                "transactionPrice": 125.50,
            },
            {
                "name": "Jane Smith",
                "share": 30000,
                "change": -5000,
                "filingDate": "2026-03-10",
                "transactionDate": "2026-03-08",
                "transactionCode": "S",
                "transactionPrice": 130.00,
            },
        ],
        "symbol": "RTX",
    }

    async with Client(mcp_server) as client:
        result = await client.call_tool("get_insider_transactions", {"symbol": "RTX"})

        result_data = json.loads(result.data)
        assert result_data["symbol"] == "RTX"
        assert result_data["count"] == 2
        assert len(result_data["transactions"]) == 2
        assert result_data["transactions"][0]["name"] == "John Doe"
        assert result_data["transactions"][0]["transaction_code"] == "P"
        assert result_data["transactions"][1]["transaction_code"] == "S"
        assert "retrieved_at" in result_data


@patch.dict(os.environ, {"FINNHUB_API_KEY": "test_api_key"})
@patch("finnhub.Client")
@pytest.mark.asyncio
async def test_get_insider_transactions_respects_limit(mock_finnhub_client, mcp_server):
    """Test that limit parameter caps the number of returned transactions."""
    mock_client = MagicMock()
    mock_finnhub_client.return_value = mock_client
    mock_client.stock_insider_transactions.return_value = {
        "data": [{"name": f"Person {i}", "share": 1000, "change": 100} for i in range(30)],
    }

    async with Client(mcp_server) as client:
        result = await client.call_tool("get_insider_transactions", {"symbol": "AAPL", "limit": 5})

        result_data = json.loads(result.data)
        assert result_data["count"] == 5


@patch.dict(os.environ, {"FINNHUB_API_KEY": "test_api_key"})
@patch("finnhub.Client")
@pytest.mark.asyncio
async def test_get_insider_sentiment_with_mock(mock_finnhub_client, mcp_server):
    """Test get_insider_sentiment returns monthly buy/sell metrics."""
    mock_client = MagicMock()
    mock_finnhub_client.return_value = mock_client
    mock_client.stock_insider_sentiment.return_value = {
        "data": [
            {"year": 2026, "month": 1, "change": 50000, "mspr": 25.5},
            {"year": 2026, "month": 2, "change": -10000, "mspr": -5.2},
            {"year": 2026, "month": 3, "change": 30000, "mspr": 15.0},
        ],
        "symbol": "RTX",
    }

    async with Client(mcp_server) as client:
        result = await client.call_tool("get_insider_sentiment", {"symbol": "RTX"})

        result_data = json.loads(result.data)
        assert result_data["symbol"] == "RTX"
        assert result_data["months_available"] == 3
        assert len(result_data["sentiment"]) == 3
        assert result_data["sentiment"][0]["year"] == 2026
        assert result_data["sentiment"][0]["month"] == 1
        assert result_data["sentiment"][0]["mspr"] == 25.5
        assert "retrieved_at" in result_data


@patch.dict(os.environ, {"FINNHUB_API_KEY": "test_api_key"})
@patch("finnhub.Client")
@pytest.mark.asyncio
async def test_get_insider_sentiment_caps_to_12_months(mock_finnhub_client, mcp_server):
    """Test that insider sentiment only returns the last 12 months."""
    mock_client = MagicMock()
    mock_finnhub_client.return_value = mock_client
    mock_client.stock_insider_sentiment.return_value = {
        "data": [{"year": 2025, "month": i, "change": 1000, "mspr": 1.0} for i in range(1, 13)]
        + [{"year": 2026, "month": i, "change": 2000, "mspr": 2.0} for i in range(1, 4)],
    }

    async with Client(mcp_server) as client:
        result = await client.call_tool("get_insider_sentiment", {"symbol": "AAPL"})

        result_data = json.loads(result.data)
        assert result_data["months_available"] == 12
        # Should be the last 12 months (2025-04 through 2026-03)
        assert result_data["sentiment"][0]["year"] == 2025
        assert result_data["sentiment"][-1]["year"] == 2026


@patch.dict(os.environ, {"FINNHUB_API_KEY": "test_api_key"})
@patch("finnhub.Client")
@pytest.mark.asyncio
async def test_get_earnings_calendar_with_symbol(mock_finnhub_client, mcp_server):
    """Test get_earnings_calendar returns earnings for a specific symbol."""
    mock_client = MagicMock()
    mock_finnhub_client.return_value = mock_client
    mock_client.earnings_calendar.return_value = {
        "earningsCalendar": [
            {
                "symbol": "RTX",
                "date": "2026-04-15",
                "quarter": 1,
                "year": 2026,
                "epsEstimate": 1.35,
                "epsActual": None,
                "revenueEstimate": 19800000000,
                "revenueActual": None,
            }
        ]
    }

    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "get_earnings_calendar",
            {"symbol": "RTX", "from_date": "2026-04-01", "to_date": "2026-04-30"},
        )

        result_data = json.loads(result.data)
        assert result_data["count"] == 1
        assert result_data["earnings"][0]["symbol"] == "RTX"
        assert result_data["earnings"][0]["date"] == "2026-04-15"
        assert result_data["earnings"][0]["eps_estimate"] == 1.35
        assert result_data["earnings"][0]["eps_actual"] is None
        assert result_data["from_date"] == "2026-04-01"
        assert result_data["to_date"] == "2026-04-30"
        assert "retrieved_at" in result_data


@patch.dict(os.environ, {"FINNHUB_API_KEY": "test_api_key"})
@patch("finnhub.Client")
@pytest.mark.asyncio
async def test_get_earnings_calendar_defaults_dates(mock_finnhub_client, mcp_server):
    """Test get_earnings_calendar uses today + 30 days when no dates given."""
    mock_client = MagicMock()
    mock_finnhub_client.return_value = mock_client
    mock_client.earnings_calendar.return_value = {"earningsCalendar": []}

    async with Client(mcp_server) as client:
        result = await client.call_tool("get_earnings_calendar", {})

        result_data = json.loads(result.data)
        assert result_data["count"] == 0
        # Dates should be populated (not empty strings)
        assert result_data["from_date"] != ""
        assert result_data["to_date"] != ""
        assert "retrieved_at" in result_data


@patch.dict(os.environ, {"FINNHUB_API_KEY": "test_api_key"})
@patch("finnhub.Client")
@pytest.mark.asyncio
async def test_get_peers_with_mock(mock_finnhub_client, mcp_server):
    """Test get_peers returns a list of similar companies."""
    mock_client = MagicMock()
    mock_finnhub_client.return_value = mock_client
    mock_client.company_peers.return_value = ["LMT", "BA", "NOC", "GD", "HII"]

    async with Client(mcp_server) as client:
        result = await client.call_tool("get_peers", {"symbol": "RTX"})

        result_data = json.loads(result.data)
        assert result_data["symbol"] == "RTX"
        assert result_data["count"] == 5
        assert "LMT" in result_data["peers"]
        assert "BA" in result_data["peers"]
        assert "retrieved_at" in result_data


@patch.dict(os.environ, {"FINNHUB_API_KEY": "test_api_key"})
@patch("finnhub.Client")
@pytest.mark.asyncio
async def test_get_peers_empty_result(mock_finnhub_client, mcp_server):
    """Test get_peers handles empty or non-list response gracefully."""
    mock_client = MagicMock()
    mock_finnhub_client.return_value = mock_client
    mock_client.company_peers.return_value = None

    async with Client(mcp_server) as client:
        result = await client.call_tool("get_peers", {"symbol": "ZZZZ"})

        result_data = json.loads(result.data)
        assert result_data["symbol"] == "ZZZZ"
        assert result_data["count"] == 0
        assert result_data["peers"] == []


@patch.dict(os.environ, {"FINNHUB_API_KEY": "test_api_key"})
@patch("finnhub.Client")
@pytest.mark.asyncio
async def test_get_company_news_with_mock(mock_finnhub_client, mcp_server):
    """Test get_company_news returns formatted news articles."""
    mock_client = MagicMock()
    mock_finnhub_client.return_value = mock_client
    mock_client.company_news.return_value = [
        {
            "headline": "RTX Wins $2B Contract",
            "summary": "RTX awarded major defense contract",
            "url": "https://example.com/rtx-contract",
            "datetime": 1711929600,
            "source": "Reuters",
        },
        {
            "headline": "RTX Q4 Earnings Preview",
            "summary": "Analysts expect strong quarter",
            "url": "https://example.com/rtx-earnings",
            "datetime": 1711843200,
            "source": "Bloomberg",
        },
    ]

    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "get_company_news",
            {"symbol": "RTX", "from_date": "2026-03-20", "to_date": "2026-03-27"},
        )

        result_data = json.loads(result.data)
        assert result_data["symbol"] == "RTX"
        assert result_data["count"] == 2
        assert len(result_data["news"]) == 2
        assert result_data["news"][0]["headline"] == "RTX Wins $2B Contract"
        assert result_data["news"][0]["source"] == "Reuters"
        assert result_data["from_date"] == "2026-03-20"
        assert result_data["to_date"] == "2026-03-27"
        assert "retrieved_at" in result_data


@patch.dict(os.environ, {"FINNHUB_API_KEY": "test_api_key"})
@patch("finnhub.Client")
@pytest.mark.asyncio
async def test_get_company_news_defaults_dates(mock_finnhub_client, mcp_server):
    """Test get_company_news defaults to last 7 days when no dates given."""
    mock_client = MagicMock()
    mock_finnhub_client.return_value = mock_client
    mock_client.company_news.return_value = []

    async with Client(mcp_server) as client:
        result = await client.call_tool("get_company_news", {"symbol": "AAPL"})

        result_data = json.loads(result.data)
        assert result_data["symbol"] == "AAPL"
        assert result_data["count"] == 0
        assert result_data["from_date"] != ""
        assert result_data["to_date"] != ""


@patch.dict(os.environ, {"FINNHUB_API_KEY": "test_api_key"})
@patch("finnhub.Client")
@pytest.mark.asyncio
async def test_get_company_news_caps_at_15(mock_finnhub_client, mcp_server):
    """Test that company news is capped at 15 articles."""
    mock_client = MagicMock()
    mock_finnhub_client.return_value = mock_client
    mock_client.company_news.return_value = [
        {"headline": f"Article {i}", "summary": "", "url": "", "datetime": 0, "source": ""}
        for i in range(30)
    ]

    async with Client(mcp_server) as client:
        result = await client.call_tool("get_company_news", {"symbol": "AAPL"})

        result_data = json.loads(result.data)
        assert result_data["count"] == 15


# --- Error handling tests for new tools ---


@pytest.mark.asyncio
async def test_get_insider_transactions_no_api_key(mcp_server):
    """Test get_insider_transactions returns error without API key."""
    with patch.dict(os.environ, {}, clear=True):
        async with Client(mcp_server) as client:
            result = await client.call_tool("get_insider_transactions", {"symbol": "AAPL"})
            result_data = json.loads(result.data)
            assert "error" in result_data


@pytest.mark.asyncio
async def test_get_earnings_calendar_no_api_key(mcp_server):
    """Test get_earnings_calendar returns error without API key."""
    with patch.dict(os.environ, {}, clear=True):
        async with Client(mcp_server) as client:
            result = await client.call_tool("get_earnings_calendar", {})
            result_data = json.loads(result.data)
            assert "error" in result_data


@pytest.mark.asyncio
async def test_get_peers_no_api_key(mcp_server):
    """Test get_peers returns error without API key."""
    with patch.dict(os.environ, {}, clear=True):
        async with Client(mcp_server) as client:
            result = await client.call_tool("get_peers", {"symbol": "AAPL"})
            result_data = json.loads(result.data)
            assert "error" in result_data
