import alpaca_client as alpaca_client
from alpaca.trading.enums import OrderSide
import time

stream = alpaca_client.StockDataStream("PKVMHGJS9OAE1W5SWCRD", "WUo8NQxuTyNBbnBJSSZgCGYOimyPYT8626BXbdVF")

async def handle_trade(trade):
    try:
        alpaca_client.get_position("FLUT")
    except Exception as e:

        print("No position in FLUT")

        try:
            alpaca_client.place_order("FLUT", 3, OrderSide.BUY)
            print("Bought 3 shares of FLUT")
            time.sleep(2)
        except Exception as e:
            print(e)
        return
    
    positions = alpaca_client.get_position("FLUT")
    print(positions.avg_entry_price, trade.bid_price)
    if (trade.bid_price - float(positions.avg_entry_price) > 0.3):
        try:
            alpaca_client.place_order("FLUT", positions.qty, OrderSide.SELL)
            print ("Succsessful trade")
        except Exception as e:
            print(e)




stream.subscribe_quotes(handle_trade, "FLUT")
runner = stream.run()

