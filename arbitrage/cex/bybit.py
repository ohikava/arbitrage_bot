import requests 
import os 
import time 
import aiohttp
from arbitrage.cex.market import Market


APIURL = "https://api.bybit.com"

class ByBit(Market):
    def __init__(self) -> None:
        super().__init__()
        self.LIMIT = 10
        self.TIME_RATE = 1
    
    def get_request_info(self, symbol: str, limit: int) -> tuple:
        path = 'v5/market/orderbook'

        params = {
        "symbol": f"{symbol}",
        "category": "spot",
        "limit": f"{limit}",
        }
        url = f"{APIURL}/{path}"

        return (url, params)

    
    def _format_data(self, data):
        res = {}
        res['bids'] = data['result']['b']
        res['asks'] = data['result']['a']
        return res 
    
    def _convert_symbols(self, symbol: str) -> str:
        return symbol.replace("/", "")

    async def load_symbols(self, session):
        self.listed_tokens = []
        
        endpoint = "/v5/market/instruments-info?category=spot"
        uri = f"{APIURL}{endpoint}"

        res = await self._send_request(uri, {}, session)

        self.requests_num += 1
        self.last_request = time.time()
        
        for symbol in res['result']['list']:
            self.listed_tokens.append(f"{symbol['baseCoin']}/{symbol['quoteCoin']}")

    

