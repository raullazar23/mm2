import alpaca_client as alpaca_client
import utils as utils
from alpaca_client import API_SECRET, API_KEY
import buy_strategy as buy_strategy
from alpaca.trading.enums import OrderSide
import time
import sys
import asyncio

stream = alpaca_client.StockDataStream(API_KEY, API_SECRET)
price_history = {}
vwap_history = {}
symbols = sys.argv[1:]


async def handle_trade(trade, symbols):
    """Processes trade events for multiple stocks."""
    global price_history, vwap_history

    symbol = trade.symbol  # Trade event will already contain the stock symbol

    if symbol not in symbols:
        return  # Ignore trades for symbols not in our list

    try:
        positions = alpaca_client.get_position(symbol)
    except Exception:
        # No position, store trade price history
        price_history.setdefault(symbol, []).append(trade.price)
        if len(price_history[symbol]) > buy_strategy.ema_long_window:
            price_history[symbol] = price_history[symbol][-buy_strategy.ema_long_window:]

        # Store VWAP history
        vwap_history.setdefault(symbol, []).append(buy_strategy.calculate_vwap(symbol))
        if len(vwap_history[symbol]) > 10:
            vwap_history[symbol] = vwap_history[symbol][-10:]

            # Check buy conditions
            if buy_strategy.check_buy_conditions(trade.price, symbol, price_history[symbol], vwap_history[symbol]):
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

    # If we already have a position, check for sell conditions
    positions = alpaca_client.get_position(symbol)
    print(f"{symbol} - Entry Price: {positions.avg_entry_price}, Current Price: {trade.price}")

    if utils.get_pnl(symbol) >= 0.4:
        try:
            alpaca_client.place_order(symbol, positions.qty, OrderSide.SELL)
            print(f"Successful trade on {symbol}")
            time.sleep(2)
        except Exception as e:
            print(e)

async def trade_callback(trade):
    """Handles incoming trade data from WebSocket."""
    await handle_trade(trade, symbols)

# Subscribe to trade updates for multiple stocks
stream.subscribe_trades(trade_callback, *symbols)
runner = stream.run()