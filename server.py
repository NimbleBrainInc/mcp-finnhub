#!/usr/bin/env python3
"""
Finnhub MCP Server - FastMCP Implementation
Financial market data and news service powered by Finnhub API
"""

import json
import os
from datetime import datetime, timezone

import finnhub
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

# Create FastMCP server
mcp = FastMCP("Finnhub MCP Server")


def get_finnhub_client(api_key: str = None) -> finnhub.Client:
    """Get Finnhub client with API key"""
    if not api_key:
        api_key = os.getenv("FINNHUB_API_KEY")
    if not api_key:
        raise ValueError("FINNHUB_API_KEY environment variable is required")
    return finnhub.Client(api_key=api_key)




@mcp.tool
def get_market_news(
    category: str = "general", min_id: str = "0", api_key: str = None
) -> str:
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
                    "datetime": datetime.fromtimestamp(
                        article.get("datetime", 0)
                    ).isoformat(),
                    "source": article.get("source", ""),
                    "category": article.get("category", ""),
                }
            )

        result = {
            "news": formatted_news,
            "category": category,
            "count": len(formatted_news),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        error_result = {
            "error": f"Error fetching market news: {str(e)}",
            "category": category,
            "timestamp": datetime.now(timezone.utc).isoformat(),
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
                datetime.fromtimestamp(quote.get("t", 0)).isoformat()
                if quote.get("t")
                else None
            ),
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        error_result = {
            "error": f"Error fetching stock quote for {symbol}: {str(e)}",
            "symbol": symbol,
            "timestamp": datetime.now(timezone.utc).isoformat(),
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
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        error_result = {
            "error": f"Error fetching company profile for {symbol}: {str(e)}",
            "symbol": symbol,
            "timestamp": datetime.now(timezone.utc).isoformat(),
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
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        error_result = {
            "error": f"Error fetching basic financials for {symbol}: {str(e)}",
            "symbol": symbol,
            "timestamp": datetime.now(timezone.utc).isoformat(),
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
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        error_result = {
            "error": f"Error fetching recommendation trends for {symbol}: {str(e)}",
            "symbol": symbol,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        return json.dumps(error_result, indent=2)


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request):
    return JSONResponse({"status": "healthy"})

def main():
    """Main entry point"""
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000,
    )


if __name__ == "__main__":
    main()
