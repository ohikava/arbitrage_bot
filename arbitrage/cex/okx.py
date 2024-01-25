from arbitrage.cex.market import Market
from dotenv import load_dotenv
import os
import hmac 
import base64
from hashlib import sha256
import time 
from arbitrage.utils.chains_mapper import chains_mapping
from datetime import datetime
import json 

load_dotenv()

APIURL = "https://www.okx.com"

class OKX(Market):
    def __init__(self) -> None:
        super().__init__()
        self.LIMIT = 40
        self.TIME_RATE = 2
        self.api_key = os.getenv("OKX_API_KEY")
        self.secret_key = os.getenv("OKX_SECRET_KEY")
        self.passphrase = os.getenv("OKX_PASSPHRASE")

        self.time_stamp = str(int(time.time() * 10 ** 3))
        self.recv_window = "5000"

    def _convert_symbols(self, symbol: str) -> str:
        return symbol.replace("/", "-")
    
    def get_request_info(self, symbol: str, limit: int) -> tuple:
        path = '/api/v5/market/books'
        uri = f"{APIURL}{path}"

        params = {
        "instId": f"{symbol}",
        "sz": f"{limit}",
        }

        return (uri, params)
    
    def _get_sign(self, payload):
        mac = hmac.new(bytes(self.secret_key, encoding='utf8'), bytes(payload, encoding='utf-8'), digestmod='sha256')
        d = mac.digest()
        return base64.b64encode(d).decode()
    
    def _format_data(self, data):
        res = {}
        res['bids'] = [[i[0], i[1]] for i in data['data'][0]['bids']]
        res['asks'] = [[i[0], i[1]] for i in data['data'][0]['asks']]
        return res 
    
    async def load_symbols(self, session):
        self.listed_tokens = []
        
        endpoint = "/api/v5/public/instruments?instType=SPOT"

        uri = f"{APIURL}{endpoint}"

        res = await self._send_request(uri, {}, session)

        for item in res['data']:
            self.listed_tokens.append(item['instId'].replace("-", "/"))

    async def load_chains(self, session):
        self.chains = {}

        endpoint = "/api/v5/asset/currencies"
        
        uri = f"{APIURL}{endpoint}"

        self.time_stamp = datetime.utcnow().isoformat(sep='T', timespec='milliseconds') + "Z"

        payload = str(self.time_stamp) + str.upper('get') + endpoint

        signature = self._get_sign(payload)
        headers = {
            "OK-ACCESS-KEY": self.api_key,
            "OK-ACCESS-SIGN": signature,
            "OK-ACCESS-TIMESTAMP": self.time_stamp,
            "OK-ACCESS-PASSPHRASE": self.passphrase,
            'CONTENT-TYPE': 'application/json'
        }

        res = await self._send_request(uri, {}, session, headers=headers)

        for item in res['data']:
            name = item['ccy']
            if name not in self.chains:
                self.chains[name] = {}

            chain = item['chain'].split('-')[-1]
            chain = chains_mapping.get(chain, chain)

            self.chains[name][chain] = {
                'deposit': item.get('canDep', None),
                'withdraw': item.get('canWd', None),
                'withdrawFee': item.get('fee', None),
                'withdrawMin': item.get('minWd', None),
                'withdrawMax': item.get('withdrawMax', None),
                'contract': item.get('contract', None),
            }