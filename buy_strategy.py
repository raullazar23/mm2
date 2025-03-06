import numpy as np
from alpaca_client import API_SECRET, API_KEY, trading_client
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestBarRequest

market_data_client = StockHistoricalDataClient(API_KEY, API_SECRET)

# Store recent prices
ema_short_window = 5
ema_long_window = 10

def calculate_ema(prices, window):
    """Calculate Exponential Moving Average (EMA)."""
    if len(prices) < window:
        return None
    return np.mean(prices[-window:])


def calculate_vwap(symbol):
    """Fetch the latest VWAP for the given symbol."""
    request = StockLatestBarRequest(symbol_or_symbols=symbol)
    latest_bar = market_data_client.get_stock_latest_bar(request)[symbol]

    return (latest_bar.high + latest_bar.low + latest_bar.close) / 3  # Approximate VWAP

def check_buy_conditions(current_price, symbol, price_history, vwap_history):
    """Determine if we should buy based on VWAP and EMA crossover."""
    if len(price_history) < ema_long_window:
        return

    short_ema = calculate_ema(price_history, ema_short_window)
    long_ema = calculate_ema(price_history, ema_long_window)
    current_price = price_history[-1]
    vwap = vwap_history[-1] if vwap_history else calculate_vwap(symbol)

    # Buy conditions:
    if short_ema > long_ema and current_price > vwap:
        return True

