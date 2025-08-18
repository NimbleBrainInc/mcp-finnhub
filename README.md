# MCP Finnhub Server

A comprehensive financial market data and news service powered by the Finnhub API. This MCP server provides real-time stock quotes, company profiles, financial metrics, analyst recommendations, and market news.

## Features

- **get_market_news**: Get latest market news by category (general, forex, crypto, merger)
- **get_stock_quote**: Get real-time stock quotes with pricing and trading data
- **get_company_profile**: Get detailed company information and profiles
- **get_basic_financials**: Get key financial metrics and ratios
- **get_recommendation_trends**: Get analyst recommendation trends and ratings

## MCP Protocol Endpoints

- `GET /health` - Health check endpoint
- `POST /mcp` - Main MCP protocol endpoint for all tool interactions
- Available tools accessible via MCP protocol:
  - `get_market_news` - Get latest market news by category
  - `get_stock_quote` - Get real-time stock quotes
  - `get_company_profile` - Get detailed company information
  - `get_basic_financials` - Get key financial metrics and ratios
  - `get_recommendation_trends` - Get analyst recommendation trends

## Configuration

### Required Environment Variables

- `FINNHUB_API_KEY` - Your Finnhub API key (get one free at [finnhub.io](https://finnhub.io))

### Optional Environment Variables

- `PORT` - Server port (default: 8000)
- `HOST` - Server host (default: 0.0.0.0)

## Development

### Requirements

- Python 3.13+
- FastMCP 2.11.2+
- uv (for dependency management)
- Finnhub API key

### Setup

```bash
# Install dependencies
uv sync

# Set your API key
export FINNHUB_API_KEY="your_api_key_here"

# Run tests with proper async support
uv run pytest

# Run server locally (streamable-http transport)
uv run python server.py
```

The server will start on `http://localhost:8000` using the streamable-http transport. All tool interactions must go through the MCP protocol endpoint at `/mcp`.

### Docker Build & Push

Use the provided Makefile for common tasks:

```bash
# Run tests
make test

# Build Docker image
make build

# Push to registry (requires Docker Hub login)
make push

# Test, build, and push
make all

# Interactive version release
make release
```

Manual Docker commands:

```bash
# Build image
docker build -t nimbletools/mcp-finnhub .

# Run container with API key
docker run -e FINNHUB_API_KEY="your_api_key" -p 8000:8000 nimbletools/mcp-finnhub

# Push to Docker Hub
docker push nimbletools/mcp-finnhub
```

## Usage Examples

All tool interactions must use the MCP protocol. Here are examples of proper MCP requests:

### Initialize MCP Session

First, establish an MCP session to initialize the connection:

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "test-client",
        "version": "1.0.0"
      }
    }
  }'
```

### List Available Tools

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list"
  }'
```

### Get Market News

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "get_market_news",
      "arguments": {
        "category": "general"
      }
    }
  }'
```

### Get Stock Quote

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "get_stock_quote",
      "arguments": {
        "symbol": "AAPL"
      }
    }
  }'
```

### Get Company Profile

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
      "name": "get_company_profile",
      "arguments": {
        "symbol": "MSFT"
      }
    }
  }'
```

**Note**: Session management is required. You must initialize the MCP session before making tool calls. Each request should use unique `id` values to track responses properly.

## Finnhub API

This server uses the [Finnhub API](https://finnhub.io) to provide financial data. You'll need a free API key to use this service.

### Free Tier Limits

- 60 API calls/minute
- Basic stock data, news, and company information
- Real-time US stock prices

### Premium Features

- Higher rate limits
- More historical data
- Advanced financial metrics
- Global market coverage

## About

Part of the [NimbleTools](https://www.nimbletools.ai) ecosystem.
From the makers of [NimbleBrain](https://www.nimblebrain.ai). 

## License

MIT License - see [LICENSE](LICENSE) for details.
