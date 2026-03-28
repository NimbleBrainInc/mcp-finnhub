#!/usr/bin/env python3
"""
Finnhub MCP Server - FastMCP Implementation
Financial market data and news service powered by Finnhub API
"""

import json
import os
from datetime import UTC, datetime
from importlib.resources import files

import finnhub
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

# Create FastMCP server
mcp = FastMCP(
    "Finnhub MCP Server",
    instructions=(
        "Before using Finnhub tools, read the skill://finnhub/usage resource "
        "for tool selection guidance and multi-step workflow patterns."
    ),
)

SKILL_CONTENT = files("mcp_finnhub").joinpath("SKILL.md").read_text()


@mcp.resource("skill://finnhub/usage")
def finnhub_skill() -> str:
    """How to effectively use Finnhub tools: tool selection, stock symbols, multi-step workflows."""
    return SKILL_CONTENT


def get_finnhub_client(api_key: str = None) -> finnhub.Client:
    """Get Finnhub client with API key"""
    if not api_key:
        api_key = os.getenv("FINNHUB_API_KEY")
    if not api_key:
        raise ValueError("FINNHUB_API_KEY environment variable is required")
    return finnhub.Client(api_key=api_key)


@mcp.tool
def get_market_news(category: str = "general", min_id: str = "0", api_key: str = None) -> str:
    """Get latest market news from Finnhub"""
    try:
        client = get_finnhub_client(api_key)
        news = client.general_news(category, min_id=min_id)

        # Format news for better readability
        formatted_news = []
        for article in news[:10]:  # Limit to 10 articles
            formatted_news.append(
                {
                    "headline": article.get("headline", ""),
                    "summary": article.get("summary", ""),
                    "url": article.get("url", ""),
                    "datetime": datetime.fromtimestamp(article.get("datetime", 0)).isoformat(),
                    "source": article.get("source", ""),
                    "category": article.get("category", ""),
                }
            )

        result = {
            "news": formatted_news,
            "category": category,
            "count": len(formatted_news),
            "timestamp": datetime.now(UTC).isoformat(),
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        error_result = {
            "error": f"Error fetching market news: {str(e)}",
            "category": category,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        return json.dumps(error_result, indent=2)


@mcp.tool
def get_stock_quote(symbol: str, api_key: str = None) -> str:
    """Get current stock quote for a symbol"""
    try:
        client = get_finnhub_client(api_key)
        quote = client.quote(symbol)

        result = {
            "symbol": symbol,
            "current_price": quote.get("c", 0),
            "change": quote.get("d", 0),
            "percent_change": quote.get("dp", 0),
            "high": quote.get("h", 0),
            "low": quote.get("l", 0),
            "open": quote.get("o", 0),
            "previous_close": quote.get("pc", 0),
            "timestamp": (
                datetime.fromtimestamp(quote.get("t", 0)).isoformat() if quote.get("t") else None
            ),
            "retrieved_at": datetime.now(UTC).isoformat(),
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        error_result = {
            "error": f"Error fetching stock quote for {symbol}: {str(e)}",
            "symbol": symbol,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        return json.dumps(error_result, indent=2)


@mcp.tool
def get_company_profile(symbol: str, api_key: str = None) -> str:
    """Get company profile information for a stock symbol"""
    try:
        client = get_finnhub_client(api_key)
        profile = client.company_profile2(symbol=symbol)

        result = {
            "symbol": symbol,
            "name": profile.get("name", ""),
            "country": profile.get("country", ""),
            "currency": profile.get("currency", ""),
            "exchange": profile.get("exchange", ""),
            "industry": profile.get("finnhubIndustry", ""),
            "logo": profile.get("logo", ""),
            "market_cap": profile.get("marketCapitalization", 0),
            "phone": profile.get("phone", ""),
            "share_outstanding": profile.get("shareOutstanding", 0),
            "ticker": profile.get("ticker", ""),
            "web_url": profile.get("weburl", ""),
            "ipo_date": profile.get("ipo", ""),
            "retrieved_at": datetime.now(UTC).isoformat(),
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        error_result = {
            "error": f"Error fetching company profile for {symbol}: {str(e)}",
            "symbol": symbol,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        return json.dumps(error_result, indent=2)


@mcp.tool
def get_basic_financials(symbol: str, metric: str = "all", api_key: str = None) -> str:
    """Get basic financial metrics for a company"""
    try:
        client = get_finnhub_client(api_key)
        financials = client.company_basic_financials(symbol, "all")

        metrics = financials.get("metric", {})

        # Key financial metrics
        key_metrics = {
            "52_week_high": metrics.get("52WeekHigh"),
            "52_week_low": metrics.get("52WeekLow"),
            "beta": metrics.get("beta"),
            "pe_ratio": metrics.get("peBasicExclExtraTTM"),
            "eps": metrics.get("epsBasicExclExtraTTM"),
            "market_cap": metrics.get("marketCapitalization"),
            "dividend_yield": metrics.get("currentDividendYieldTTM"),
            "roe": metrics.get("roeTTM"),
            "roa": metrics.get("roaTTM"),
            "debt_to_equity": metrics.get("totalDebt/totalEquityQuarterly"),
            "current_ratio": metrics.get("currentRatioQuarterly"),
            "gross_margin": metrics.get("grossMarginTTM"),
            "operating_margin": metrics.get("operatingMarginTTM"),
            "net_margin": metrics.get("netProfitMarginTTM"),
        }

        result = {
            "symbol": symbol,
            "key_metrics": key_metrics,
            "all_metrics_available": len(metrics) > 0,
            "total_metrics": len(metrics),
            "retrieved_at": datetime.now(UTC).isoformat(),
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        error_result = {
            "error": f"Error fetching basic financials for {symbol}: {str(e)}",
            "symbol": symbol,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        return json.dumps(error_result, indent=2)


@mcp.tool
def get_recommendation_trends(symbol: str, api_key: str = None) -> str:
    """Get analyst recommendation trends for a stock"""
    try:
        client = get_finnhub_client(api_key)
        recommendations = client.recommendation_trends(symbol)

        # Format recommendations for better readability
        formatted_recs = []
        for rec in recommendations:
            formatted_recs.append(
                {
                    "period": rec.get("period", ""),
                    "strong_buy": rec.get("strongBuy", 0),
                    "buy": rec.get("buy", 0),
                    "hold": rec.get("hold", 0),
                    "sell": rec.get("sell", 0),
                    "strong_sell": rec.get("strongSell", 0),
                }
            )

        result = {
            "symbol": symbol,
            "recommendations": formatted_recs,
            "periods_available": len(formatted_recs),
            "retrieved_at": datetime.now(UTC).isoformat(),
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        error_result = {
            "error": f"Error fetching recommendation trends for {symbol}: {str(e)}",
            "symbol": symbol,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        return json.dumps(error_result, indent=2)


@mcp.tool
def get_insider_transactions(symbol: str, limit: int = 20, api_key: str = None) -> str:
    """Get insider transactions (SEC Form 4) for a stock symbol"""
    try:
        client = get_finnhub_client(api_key)
        data = client.stock_insider_transactions(symbol)

        transactions = data.get("data", [])[:limit]
        formatted = []
        for txn in transactions:
            formatted.append(
                {
                    "name": txn.get("name", ""),
                    "share": txn.get("share", 0),
                    "change": txn.get("change", 0),
                    "filing_date": txn.get("filingDate", ""),
                    "transaction_date": txn.get("transactionDate", ""),
                    "transaction_code": txn.get("transactionCode", ""),
                    "transaction_price": txn.get("transactionPrice", 0),
                }
            )

        result = {
            "symbol": symbol,
            "transactions": formatted,
            "count": len(formatted),
            "retrieved_at": datetime.now(UTC).isoformat(),
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        error_result = {
            "error": f"Error fetching insider transactions for {symbol}: {str(e)}",
            "symbol": symbol,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        return json.dumps(error_result, indent=2)


@mcp.tool
def get_insider_sentiment(symbol: str, api_key: str = None) -> str:
    """Get aggregated insider sentiment (monthly buy/sell metrics) for a stock"""
    try:
        client = get_finnhub_client(api_key)
        data = client.stock_insider_sentiment(
            symbol, "2020-01-01", datetime.now().strftime("%Y-%m-%d")
        )

        records = data.get("data", [])
        # Return last 12 months
        recent = records[-12:] if len(records) > 12 else records

        formatted = []
        for rec in recent:
            formatted.append(
                {
                    "year": rec.get("year", 0),
                    "month": rec.get("month", 0),
                    "change": rec.get("change", 0),
                    "mspr": rec.get("mspr", 0),
                }
            )

        result = {
            "symbol": symbol,
            "sentiment": formatted,
            "months_available": len(formatted),
            "retrieved_at": datetime.now(UTC).isoformat(),
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        error_result = {
            "error": f"Error fetching insider sentiment for {symbol}: {str(e)}",
            "symbol": symbol,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        return json.dumps(error_result, indent=2)


@mcp.tool
def get_earnings_calendar(
    from_date: str = "", to_date: str = "", symbol: str = "", api_key: str = None
) -> str:
    """Get earnings calendar with upcoming and recent earnings dates, EPS estimates and actuals"""
    try:
        client = get_finnhub_client(api_key)

        if not from_date:
            from_date = datetime.now().strftime("%Y-%m-%d")
        if not to_date:
            # Default to 30 days out
            from datetime import timedelta

            to_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        data = client.earnings_calendar(
            _from=from_date, to=to_date, symbol=symbol if symbol else None
        )

        events = data.get("earningsCalendar", [])
        formatted = []
        for event in events[:50]:
            formatted.append(
                {
                    "symbol": event.get("symbol", ""),
                    "date": event.get("date", ""),
                    "quarter": event.get("quarter", 0),
                    "year": event.get("year", 0),
                    "eps_estimate": event.get("epsEstimate"),
                    "eps_actual": event.get("epsActual"),
                    "revenue_estimate": event.get("revenueEstimate"),
                    "revenue_actual": event.get("revenueActual"),
                }
            )

        result = {
            "earnings": formatted,
            "from_date": from_date,
            "to_date": to_date,
            "count": len(formatted),
            "retrieved_at": datetime.now(UTC).isoformat(),
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        error_result = {
            "error": f"Error fetching earnings calendar: {str(e)}",
            "timestamp": datetime.now(UTC).isoformat(),
        }
        return json.dumps(error_result, indent=2)


@mcp.tool
def get_peers(symbol: str, api_key: str = None) -> str:
    """Get list of peer/similar companies for a stock symbol"""
    try:
        client = get_finnhub_client(api_key)
        peers = client.company_peers(symbol)

        result = {
            "symbol": symbol,
            "peers": peers if isinstance(peers, list) else [],
            "count": len(peers) if isinstance(peers, list) else 0,
            "retrieved_at": datetime.now(UTC).isoformat(),
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        error_result = {
            "error": f"Error fetching peers for {symbol}: {str(e)}",
            "symbol": symbol,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        return json.dumps(error_result, indent=2)


@mcp.tool
def get_company_news(
    symbol: str, from_date: str = "", to_date: str = "", api_key: str = None
) -> str:
    """Get recent news articles for a specific company"""
    try:
        client = get_finnhub_client(api_key)

        if not from_date:
            from datetime import timedelta

            from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        if not to_date:
            to_date = datetime.now().strftime("%Y-%m-%d")

        news = client.company_news(symbol, _from=from_date, to=to_date)

        formatted = []
        for article in news[:15]:
            formatted.append(
                {
                    "headline": article.get("headline", ""),
                    "summary": article.get("summary", ""),
                    "url": article.get("url", ""),
                    "datetime": (
                        datetime.fromtimestamp(article.get("datetime", 0)).isoformat()
                        if article.get("datetime")
                        else None
                    ),
                    "source": article.get("source", ""),
                }
            )

        result = {
            "symbol": symbol,
            "news": formatted,
            "count": len(formatted),
            "from_date": from_date,
            "to_date": to_date,
            "retrieved_at": datetime.now(UTC).isoformat(),
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        error_result = {
            "error": f"Error fetching company news for {symbol}: {str(e)}",
            "symbol": symbol,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        return json.dumps(error_result, indent=2)


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request):
    return JSONResponse({"status": "healthy"})


# ASGI entrypoint (nimbletools-core container deployment)
app = mcp.http_app()

# Stdio entrypoint (mpak / Claude Desktop)
if __name__ == "__main__":
    mcp.run()
