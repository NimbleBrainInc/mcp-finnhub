"""Test configuration and fixtures for finnhub MCP server."""

import pytest
import os
import sys

# Add parent directory to path to import server
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import mcp

@pytest.fixture
def mcp_server():
    """Return the MCP server instance"""
    return mcp