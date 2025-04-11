import alpaca_client as alpaca_client
import utils as utils
from alpaca_client import API_SECRET, API_KEY, trading_client
import buy_strategy as buy_strategy
import sys
import json

stream = alpaca_client.StockDataStream(API_KEY, API_SECRET)
price_history = {}
vwap_history = {}

# Load JSON config
with open("symbols_quant.json", "r") as file:
    config = json.load(file)

initial_symbols = config["stocks"]



async def handle_trade(trade, symbols):
    """Processes trade events for multiple stocks."""
    global price_history, vwap_history

    should_skip_sell_iteration = False
    symbol = trade.symbol  # Trade event will already contain the stock symbol
    open_positions = alpaca_client.get_positions()
    if len(open_positions) < 5:
        if utils.is_last_half_hour_trade_day(trading_client):
            print("Last half hour of trading, skipping buy.")
        else:    
            try:
                positions = alpaca_client.get_position(symbol)
                should_skip_sell_iteration = True
            except Exception as e:
                buy_strategy.buy_stock(symbol, price_history, vwap_history, trade)
                return
        
    if (should_skip_sell_iteration):
        alpaca_client.check_selling_condition(symbol, trade, alpaca_client)
        return

    for open_position in open_positions:
        if open_position.symbol == symbol:
            # If we already have a position, check for sell conditions
            alpaca_client.check_selling_condition(symbol, trade, alpaca_client)
    


async def trade_callback(trade):
    """Handles incoming trade data from WebSocket."""
    await handle_trade(trade, symbols)

symbols = alpaca_client.validate_symbols(initial_symbols)
if not symbols:
    print("No valid symbols found.")
    sys.exit(1)
stream.subscribe_trades(trade_callback, *symbols)
stream.run()