from arbitrage.observers.observer import Observer
import requests
import json 
from dotenv import load_dotenv
import os 

URL = os.getenv("BOT_URL")

class TelegramBot(Observer):
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
        url = f"{URL}/opportunity"
        body = {
            "cex_bid": cex_bid,
            "cex_ask": cex_ask,
            "bid_price": bid_price,
            "ask_price": ask_price,
            "spread": spread,
            "symbols": symbols,
            "bid_liquidity": bid_liquidity,
            "ask_liquidity": ask_liquidity,
            "chains": chains,
            "withdraw_fee": withdraw_fee,
            "ask_trade_fee": ask_trade_fee,
            "bid_trade_fee": bid_trade_fee,
            "bid_price_2": bid_price_2,
            "ask_price_2": ask_price_2,
            "spread_2": spread_2
        }
        res = requests.post(url, data=json.dumps(body))