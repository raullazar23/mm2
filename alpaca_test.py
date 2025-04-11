import alpaca_client as alpaca_client
import utils as utils
from alpaca_client import API_SECRET, API_KEY
import buy_strategy as buy_strategy
import sys

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
        buy_strategy.buy_stock(symbol, price_history, vwap_history, trade)
        return

    # If we already have a position, check for sell conditions
    alpaca_client.check_selling_condition(symbol, trade)


async def trade_callback(trade):
    """Handles incoming trade data from WebSocket."""
    await handle_trade(trade, symbols)

stream.subscribe_trades(trade_callback, *symbols)
stream.run()