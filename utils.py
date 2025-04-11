from datetime import datetime, timedelta
import time
import json
import asyncio
    
# Load JSON config
with open("symbols_quant.json", "r") as file:
    config = json.load(file)

stocks = config["stocks"]

# Function to get quantity by symbol
def get_quantity(symbol):
    return stocks.get(symbol, "Symbol not found")

def check_trading_hours(client):
    clock = client.get_clock()
    now = clock.timestamp
    timeframe = (clock.next_open - clock.next_close).total_seconds()
    if clock.is_open:
        today_open = (clock.next_close - now).total_seconds()
        if (timeframe - today_open) <= 1800:
            return True
    return False

def is_last_half_hour_trade_day(client):
    clock = client.get_clock()
    now = clock.timestamp
    if clock.is_open:
        last_half_hour = (now - clock.next_close).total_seconds() <= 900 # 15 minutes
        return last_half_hour
    return False