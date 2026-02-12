"""Test configuration and fixtures for finnhub MCP server."""

import pytest

from mcp_finnhub.server import mcp


@pytest.fixture
def mcp_server():
    """Return the MCP server instance."""
    return mcp
