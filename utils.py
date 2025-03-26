from datetime import datetime
from alpaca_client import trading_client
import pytz
import time
import json

# Define Eastern Time Zone
eastern = pytz.timezone("US/Eastern")

# Get current time in Eastern Time
now = datetime.now(eastern).time()

# Define market open and close times
market_open = datetime.strptime("09:30", "%H:%M").time()
market_close = datetime.strptime("16:00", "%H:%M").time()


def is_trading_hours():
    if market_open <= now <= market_close:
        return True
    else:
        return False
    

def check_trading_hours():
    print("Verifying trading hours")
    if not is_trading_hours():
        print("Not trading hours")
        time.sleep(600)
        return
    
# Load JSON config
with open("symbols_quant.json", "r") as file:
    config = json.load(file)

stocks = config["stocks"]

# Function to get quantity by symbol
def get_quantity(symbol):
    return stocks.get(symbol, "Symbol not found")

def get_pnl(symbol):
    try:
        position = trading_client.get_open_position(symbol)
        
        # Extract P&L data
        unrealized_pl = float(position.unrealized_pl)
        realized_pl = float(position.realized_pl)
        total_pl = unrealized_pl + realized_pl
        
        return total_pl
    except Exception as e:
        print(f"Error retrieving P&L for {symbol}: {e}")
        return None