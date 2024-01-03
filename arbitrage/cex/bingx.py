from arbitrage.cex.market import Market
import os 
import requests
import hmac 
from hashlib import sha256
from dotenv import load_dotenv
import aiohttp 
import time 
import json 

load_dotenv()

APIURL = "https://open-api.bingx.com"

class BingX(Market):
    def __init__(self) -> None:
        super().__init__()
        self.api_key = os.getenv("BINGX_API_KEY")
        self.secret_key = os.getenv("BINGX_SECRET_KEY")
        self.LIMIT = 10
        self.TIME_RATE = 1

    def _get_sign(self, payload):
        signature = hmac.new(self.secret_key.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
        return signature

    def get_request_info(self, symbol: str, limit: int) -> tuple:
        params = {
        "symbol": symbol,
        "limit": f"{limit}",
        }

        uri = f"{APIURL}/openApi/swap/v2/quote/depth"
               
        return uri, params 
    
    def _praseParam(self, paramsMap):
        sortedKeys = sorted(paramsMap)
        paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
        return paramsStr+"&timestamp="+str(int(time.time() * 1000))
    
    async def _send_request(self, uri: str, params: dict, session: aiohttp.ClientSession):
        self.check_time_restrictions()

        params_str = self._praseParam(params)
        headers = {
            'X-BX-APIKEY': self.api_key,
        }

        uri = f"{uri}?{params_str}&signature={self._get_sign(params_str)}"

        async with session.get(uri, headers=headers, data={}) as response:
            if self.check_response(response):
                return await response.json()

    def _convert_symbols(self, symbol: str) -> str:
        return symbol.replace('/', '-')
    
    