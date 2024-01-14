import logging 
from arbitrage.observers.observer import Observer
from datetime import datetime

class Logger(Observer):
    def opportunity(
        self,
        cex_bid:str,
        cex_ask:str,
        bid_price:str,
        ask_price:str,
        spread:str,
        bid_liquidity:str,
        ask_liquidity:str,
        symbols:str,
        chains: list,
        withdraw_fee: float,
        ask_trade_fee: float,
        bid_trade_fee: float,
        bid_price_2: str,
        ask_price_2: str,
        spread_2: str
    ):
        logging.info(f"{symbols} {cex_ask}: {ask_price} -> {cex_bid}: {bid_price}, spread: {round(float(spread)*100, 5)}%, ask_liquidity: {ask_liquidity}, bid_liquidity: {bid_liquidity}")