from arbitrage.observers.observer import Observer
import requests
import json 
from dotenv import load_dotenv
import os 

URL = os.getenv("BOT_URL")

class TelegramBot(Observer):
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
        url = f"{URL}/opportunity"
        body = {
            "cex_bid": bid,
            "cex_ask": ask,
            "bid_price": bid_price,
            "ask_price": ask_price,
            "spread": spread,
            "symbol": symbol,
            "bid_liquidity": bid_liquidity,
            "ask_liquidity": ask_liquidity
        }
        res = requests.post(url, data=json.dumps(body))