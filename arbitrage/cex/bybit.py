import requests 
import os 
import time 
import aiohttp
from arbitrage.cex.market import Market
from arbitrage.utils.chains_mapper import chains_mapping
import hmac 
from hashlib import sha256 

from dotenv import load_dotenv

load_dotenv()


APIURL = "https://api.bybit.com"


class ByBit(Market):
    def __init__(self) -> None:
        super().__init__()
        self.LIMIT = 10
        self.TIME_RATE = 1
        self.api_key = os.getenv("BYBIT_API_KEY")
        self.secret_key = os.getenv("BYBIT_SECRET_KEY")
        self.recv_window = "10000"
    
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
    
    def _get_sign(self, payload):
        param_str= str(self.time_stamp) + self.api_key + self.recv_window + payload
        hash = hmac.new(bytes(self.secret_key, "utf-8"), param_str.encode("utf-8"), sha256)
        signature = hash.hexdigest()
        return signature

    async def load_symbols(self, session):
        self.listed_tokens = []
        
        endpoint = "/v5/market/instruments-info?category=spot"
        uri = f"{APIURL}{endpoint}"

        res = await self._send_request(uri, {}, session)

        self.requests_num += 1
        self.last_request = time.time()
        
        for symbol in res['result']['list']:
            self.listed_tokens.append(f"{symbol['baseCoin']}/{symbol['quoteCoin']}")
    
    async def load_chains(self, session):
        self.chains = {}

        endpoint = "/v5/asset/coin/query-info"
        uri = f"{APIURL}{endpoint}"

        self.time_stamp = str(int(time.time() * 10 ** 3))

        headers = {
           "X-BAPI-API-KEY": self.api_key,
           "X-BAPI-SIGN": self._get_sign(''),
           "X-BAPI-TIMESTAMP": self.time_stamp,
           "X-BAPI-RECV-WINDOW": self.recv_window
        }

        res = await self._send_request(uri, {}, session, headers=headers)
        self.requests_num += 1
        self.last_request = time.time()

        for chain in res['result']['rows']:
            networkList = chain['chains']
            self.chains[chain['coin']] = dict()

            for network in networkList:
                formated_name = chains_mapping.get(network['chain'], network['chain'])
                self.chains[chain['coin']][formated_name] = {
                    'deposit': bool(network.get('chainDeposit', None)),
                    'withdraw': bool(network.get('chainWithdraw', None)),
                    'withdrawFee': network.get('withdrawFee', None),
                    'withdrawMin': network.get('withdrawMin', None),
                    'withdrawMax': network.get('withdrawMax', None),
                    'contract': network.get('contract', None),
                }
    




