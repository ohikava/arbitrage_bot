import logging 
from arbitrage.observers.observer import Observer
from datetime import datetime

class Logger(Observer):
    def __init__(self):
        # self.logger.addHandler(logging.StreamHandler())
        logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO, filename=f"logs/{datetime.today().strftime('%Y-%m-%d')}.txt")

    def opportunity(
        self,
        bid:str,
        ask:str,
        bid_price:str,
        ask_price:str,
        spread:str,
        liquidity:str,
        symbol:str
    ):
    
        logging.info(f"{symbol} {ask}: {ask_price} -> {bid}: {bid_price}, spread: {round(float(spread)*100, 5)}%, liquidty: {liquidity}")