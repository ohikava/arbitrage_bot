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
    def _send_request(self, method, endpoint, params):
        url = f"{APIURL}/{endpoint}"
  
        response = requests.request(method, url, params=params)
        
        return response.json()
    
    def get_symbol_depth(self, symbol: str) -> float:
        path = '/v5/market/orderbook'

        method = "GET"
        params = {
        "symbol": f"{symbol}",
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


