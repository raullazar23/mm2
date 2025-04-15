import numpy as np
import pandas as pd
import time
import utils as utils
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from alpaca.trading.enums import OrderSide
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestBarRequest

import alpaca_client as alpaca_client
from alpaca_client import API_KEY, API_SECRET, trading_client

market_data_client = StockHistoricalDataClient(API_KEY, API_SECRET)

# Configurable strategy parameters
ema_short_window = 5
ema_long_window = 10
rsi_window = 14
resistance_lookback = 12
rsi_lower = 45
rsi_upper = 55


def calculate_ema(prices, window):
    if len(prices) < window:
        return None
    prices_series = pd.Series(prices)
    ema = EMAIndicator(close=prices_series, window=window)
    return float(ema.ema_indicator().iloc[-1])


def calculate_rsi(prices):
    if len(prices) < rsi_window:
        return None
    prices_series = pd.Series(prices)
    rsi = RSIIndicator(close=prices_series, window=14)
    rsi_value = float(rsi.rsi().iloc[-1])
    return rsi_value


def calculate_vwap(symbol):
    try:
        request = StockLatestBarRequest(symbol_or_symbols=symbol)
        latest_bar = market_data_client.get_stock_latest_bar(request)[symbol]
        return (latest_bar.high + latest_bar.low + latest_bar.close) / 3
    except Exception as e:
        print(f"VWAP fetch failed for {symbol}: {e}")
        return None


def detect_resistance(prices, lookback=10, tolerance=0.0015):
    if len(prices) < lookback:
        return []
    resistance_levels = []
    for i in range(1, lookback - 1):
        if prices[-i] > prices[-i-1] and prices[-i] > prices[-i+1]:
            resistance_levels.append(prices[-i])
    # Cluster similar resistance levels
    clustered = []
    for level in sorted(resistance_levels):
        if not clustered or abs(level - clustered[-1]) / clustered[-1] > tolerance:
            clustered.append(level)
    return clustered


def is_breaking_resistance(price, resistance_levels, tolerance=0.0015):
    for r in resistance_levels:
        if abs(price - r) / r < tolerance:
            return True
    return False


def check_buy_conditions(current_price, symbol, price_history, vwap_history):
    if len(price_history) < ema_long_window or len(vwap_history) < 1:
        return False

    short_ema = calculate_ema(price_history, ema_short_window)
    long_ema = calculate_ema(price_history, ema_long_window)
    rsi = calculate_rsi(price_history)
    vwap = vwap_history[-1]
    resistance_levels = detect_resistance(price_history, resistance_lookback)

    if None in (short_ema, long_ema, rsi, vwap):
        return False

    meets_conditions = (
        short_ema > long_ema and
        current_price > vwap and
        rsi_lower <= rsi <= rsi_upper and
        is_breaking_resistance(current_price, resistance_levels)
    )

    print(f"{symbol} | EMA: {short_ema:.2f}/{long_ema:.2f} | RSI: {rsi:.2f} | VWAP: {vwap:.2f} | Price: {current_price:.2f} | Resistance: {resistance_levels} | Buy: {meets_conditions}")
    return meets_conditions


def buy_stock(symbol, price_history, vwap_history, trade):
    if utils.check_trading_hours(trading_client):
        print(f"Trade ignored for {symbol} during first half hour of trading.")
        return

    price_history.setdefault(symbol, []).append(trade.price)
    if len(price_history[symbol]) > ema_long_window + 5:
        price_history[symbol] = price_history[symbol][-ema_long_window - 5:]

    vwap_history.setdefault(symbol, []).append(calculate_vwap(symbol))
    if len(vwap_history[symbol]) > 10:
        vwap_history[symbol] = vwap_history[symbol][-10:]

        if check_buy_conditions(trade.price, symbol, price_history[symbol], vwap_history[symbol]):
            try:
                qty = utils.get_quantity(symbol)
                alpaca_client.place_order(symbol, qty, OrderSide.BUY)
                print(f"✓ BUY order executed for {symbol} at ${trade.price}")
                time.sleep(2)
            except Exception as e:
                print(f"Buy failed for {symbol}: {e}")
        else:
            print(f"× Buy conditions not met for {symbol}")
    else:
        print(f"Waiting for more data to evaluate {symbol}")
