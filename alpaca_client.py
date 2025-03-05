from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest
from alpaca.trading.enums import TimeInForce, QueryOrderStatus
from alpaca.data.live import StockDataStream


trading_client = TradingClient("PKVMHGJS9OAE1W5SWCRD", "WUo8NQxuTyNBbnBJSSZgCGYOimyPYT8626BXbdVF")
stream = StockDataStream("PKVMHGJS9OAE1W5SWCRD", "WUo8NQxuTyNBbnBJSSZgCGYOimyPYT8626BXbdVF")


def get_positions():
    positions = trading_client.get_all_positions()
    return positions

def get_position(symbol):
    position = trading_client.get_open_position(symbol)
    return position

def get_orders():
    request_params = GetOrdersRequest(
        status=QueryOrderStatus.OPEN,
    )
    orders = trading_client.get_orders(request_params)
    return orders

def place_order(symbol, qty, side):
    try:
        market_order_data = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side,
            time_in_force=TimeInForce.GTC,
        )
        trading_client.submit_order(market_order_data)
        return market_order_data.client_order_id, market_order_data.symbol, market_order_data.qty, market_order_data.side
    except Exception as e:
        print(e)

def get_account():
    account = trading_client.get_account()
    return account

def get_asset(symbol):
    asset = trading_client.get_asset(symbol)
    return asset

def get_assets():
    assets = trading_client.get_assets()
    return assets

def close_position(symbol):
    try:
        trading_client.close_position(symbol)
    except Exception as e:
        print(e)