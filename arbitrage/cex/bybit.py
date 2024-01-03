import requests 
import os 
import time 

from arbitrage.cex.market import Market


APIURL = "https://api.bybit.com"

class ByBit(Market):
    def __init__(self) -> None:
        super().__init__()
        self.LIMIT = 10
        self.TIME_RATE = 1

    def _send_request(self, method, endpoint, params):
        url = f"{APIURL}/{endpoint}"
        
        self.check_time_restrictions()
        response = requests.request(method, url, params=params)
        self.requests_num += 1
        self.last_request = time.time()
        
        if self.check_response(response):
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


