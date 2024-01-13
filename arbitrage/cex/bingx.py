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

chains_formater = {}

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
    
    # async def _send_request(self, uri: str, params: dict, session: aiohttp.ClientSession):
    #     self.check_time_restrictions()

    #     params_str = self._praseParam(params)
    #     headers = {
    #         'X-BX-APIKEY': self.api_key,
    #     }

    #     uri = f"{uri}?{params_str}&signature={self._get_sign(params_str)}"

    #     async with session.get(uri, headers=headers, data={}) as response:
    #         if self.check_response(response):
    #             return await response.json()

    def _convert_symbols(self, symbol: str) -> str:
        return symbol.replace('/', '-')
    
    async def load_symbols(self, session):
        self.listed_tokens = []
        
        endpoint = "/openApi/swap/v2/quote/ticker"
        uri = f"{APIURL}{endpoint}"

        headers = {
            'X-BX-APIKEY': self.api_key,
        }

        params_str = self._praseParam({})

        uri = f"{uri}?{params_str}&signature={self._get_sign(params_str)}"

        res = await self._send_request(uri, {}, session, headers=headers)

        self.requests_num += 1
        self.last_request = time.time()

        for symbol in res['data']:
            pair = symbol['symbol'].split("-")
            self.listed_tokens.append(f"{pair[0]}/{pair[1]}")

        print(len(self.listed_tokens))

    async def load_chains(self, session):
        self.chains = {}

        endpoint = "/openApi/wallets/v1/capital/config/getall"
        uri = f"{APIURL}{endpoint}"

        params = {
            'recvWindow': 10000
        }

        headers = {
            'X-BX-APIKEY': self.api_key,
        }
        
        params_str = self._praseParam(params)

        uri = f"{uri}?{params_str}&signature={self._get_sign(params_str)}"

        res = await self._send_request(uri, params, session, headers=headers)

        self.requests_num += 1
        self.last_request = time.time()

        for chain in res['data']:
            networkList = chain['networkList']
            self.chains[chain['coin']] = dict()

            for network in networkList:
                formated_name = chains_formater.get(network['network'], network['network'])
                self.chains[chain['coin']][formated_name] = {
                    'deposit': bool(network.get('depositEnable', None)),
                    'withdraw': bool(network.get('withdrawEnable', None)),
                    'withdrawFee': network.get('withdrawFee', None),
                    'withdrawMin': network.get('withdrawMin', None),
                    'withdrawMax': network.get('withdrawMax', None),
                    'contract': network.get('contract', None),
                }

