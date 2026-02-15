# Finnhub

## Critical: Reuse Prior Results

Follow-up questions ("what's the market cap?", "what do analysts say?") should use data from earlier tool responses before making new calls. If you already fetched a company profile or financials, surface that data directly.

## Tool Selection

| Intent | Tool |
|--------|------|
| Latest news headlines | `get_market_news(category)` |
| Current stock price | `get_stock_quote(symbol)` |
| Company background | `get_company_profile(symbol)` |
| Financial metrics (P/E, margins, etc.) | `get_basic_financials(symbol)` |
| Analyst buy/sell ratings | `get_recommendation_trends(symbol)` |

## Stock Symbols

Use uppercase US ticker symbols: `AAPL`, `MSFT`, `GOOGL`, `TSLA`.

For non-US stocks, use the exchange-suffixed format the user provides.

## News Categories

`get_market_news` accepts: `general`, `forex`, `crypto`, `merger`.

Default is `general`. Match the category to the user's intent. If results seem sparse or irrelevant, try a different category. Use `min_id` from the last article to paginate for more results.

## Multi-Step Workflows

**"Should I invest in X?"** or **"Tell me about X stock"**:
1. `get_company_profile(symbol)` for company context
2. `get_stock_quote(symbol)` for current price
3. `get_basic_financials(symbol)` for valuation metrics
4. `get_recommendation_trends(symbol)` for analyst consensus

**"What's happening in the market?"**:
1. `get_market_news(category="general")` for headlines

## Key Metrics from get_basic_financials

The response includes pre-extracted key metrics: P/E ratio, EPS, market cap, dividend yield, ROE, ROA, debt-to-equity, margins (gross, operating, net), 52-week high/low, beta, and current ratio. Use these directly rather than parsing `all_metrics`.
