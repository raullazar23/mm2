import numpy as np
import alpaca_client as alpaca_client
import utils as utils
import time
from alpaca.trading.enums import OrderSide
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


def buy_stock(symbol, price_history, vwap_history, trade):
        if utils.check_trading_hours(trading_client):
            print(f"Trade ignored for {symbol} during first half hour of trading.")
            return
     # No position, store trade price history
        price_history.setdefault(symbol, []).append(trade.price)
        if len(price_history[symbol]) > ema_long_window:
            price_history[symbol] = price_history[symbol][-ema_long_window:]

        # Store VWAP history
        vwap_history.setdefault(symbol, []).append(calculate_vwap(symbol))
        if len(vwap_history[symbol]) > 10:
            vwap_history[symbol] = vwap_history[symbol][-10:]

            # Check buy conditions
            if check_buy_conditions(trade.price, symbol, price_history[symbol], vwap_history[symbol]):
                try:
                    alpaca_client.place_order(symbol, utils.get_quantity(symbol) , OrderSide.BUY)
                    print(f"Bought 3 shares of {symbol}")
                    time.sleep(2)
                except Exception as e:
                    print(e)
            else:
                print(f"No buy conditions met for {symbol}: {vwap_history[symbol]}")
        else:
            print(f"Not enough data for buy conditions for {symbol}")
        return
