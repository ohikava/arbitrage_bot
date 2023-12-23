import requests 
import os 
from dotenv import load_dotenv
import time 
import hmac
import hashlib
from arbitrage.cex.market import Market

load_dotenv()  


APIURL = "https://api.bybit.com"

class ByBit(Market):
    def __init__(self) -> None:
        super().__init__()
        self.LIMIT = 120
        self.TIME_RATE = 5

    def _send_request(self, method, endpoint, params):
        url = f"{APIURL}/{endpoint}"
        
        if self.requests_num > 120 and time.time() - self.last_request < self.TIME_RATE:
            print(self.TIME_RATE - time.time() + self.last_request + 1)
            time.sleep(self.TIME_RATE - time.time() + self.last_request + 1)
            self.requests_num = 0

        response = requests.request(method, url, params=params)
        self.requests_num += 1
        self.last_request = time.time()
        
        return response.json()
    
    def get_symbol_depth(self, symbol: str) -> float:
        path = '/v5/market/orderbook'

        method = "GET"
        params = {
        "symbol": f"{self._convert_symbol(symbol)}",
        "category": "spot",
        "limit": "100",
        }

        res_json = self._send_request(method, path, params)
        res = self._format_data(res_json)

        return res
    
    def _format_data(self, data):
        res = {}
        res['bids'] = data['result']['b']
        res['asks'] = data['result']['a']
        return res 
    
    def _convert_symbol(self, symbol: str) -> str:
        return symbol.replace("/", "")


