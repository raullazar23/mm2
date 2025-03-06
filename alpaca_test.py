import alpaca_client as alpaca_client
from alpaca_client import API_SECRET, API_KEY
import buy_strategy as buy_strategy
from alpaca.trading.enums import OrderSide
import time

stream = alpaca_client.StockDataStream(API_KEY, API_SECRET)
price_history = []
vwap_history = []


async def handle_trade(trade):
    try:
        alpaca_client.get_position("FLUT")
    except Exception as e:
        global price_history, vwap_history
        print("No position in FLUT")
        # Store price history
        price_history.append(trade.bid_price)
        if len(price_history) > buy_strategy.ema_long_window:
            price_history = price_history[-buy_strategy.ema_long_window:]

        # Update VWAP history
        vwap_history.append(buy_strategy.calculate_vwap("FLUT"))
        if len(vwap_history) > 10:
            vwap_history = vwap_history[-10:]
            if buy_strategy.check_buy_conditions(trade.bid_price, "FLUT", price_history, vwap_history):
                try:
                    alpaca_client.place_order("FLUT", 3, OrderSide.BUY)
                    print("Bought 3 shares of FLUT")
                    time.sleep(2)
                except Exception as e:
                    print(e)
            else :
                print("No buy conditions met: ", vwap_history)
        else:
            print("Not enough data for buy conditions")
        return
    
    positions = alpaca_client.get_position("FLUT")
    print(positions.avg_entry_price, trade.bid_price)
    if (trade.bid_price - float(positions.avg_entry_price) >= 0.25):
        try:
            alpaca_client.place_order("FLUT", positions.qty, OrderSide.SELL)
            print ("Succsessful trade")
        except Exception as e:
            print(e)




stream.subscribe_quotes(handle_trade, "FLUT")
runner = stream.run()

