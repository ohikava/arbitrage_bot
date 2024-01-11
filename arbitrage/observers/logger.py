import logging 
from arbitrage.observers.observer import Observer
from datetime import datetime

class Logger(Observer):
    def opportunity(
        self,
        bid:str,
        ask:str,
        bid_price:str,
        ask_price:str,
        spread:str,
        bid_liquidity:str,
        ask_liquidity:str,
        symbol:str
    ):

        logging.info(f"{symbol} {ask}: {ask_price} -> {bid}: {bid_price}, spread: {round(float(spread)*100, 5)}%, ask_liquidity: {ask_liquidity}, bid_liquidity: {bid_liquidity}")