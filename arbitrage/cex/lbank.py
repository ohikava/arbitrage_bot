from arbitrage.cex.market import Market
from arbitrage.utils.chains_mapper import chains_mapping
import aiohttp
import time
import hmac 
from hashlib import sha256
import os 
from dotenv import load_dotenv

load_dotenv()

APIURL = "https://api.lbkex.com/"

class LBank(Market):
    def __init__(self) -> None:
        super().__init__()
        self.LIMIT = 600
        self.TIME_RATE = 60
        # self.api_key = os.getenv("BINANCE_API_KEY")
        # self.secret_key = os.getenv("BINANCE_SECRET_KEY")
        self.time_stamp = str(int(time.time() * 10 ** 3))
        self.recv_window = "5000"
    
    def get_request_info(self, symbol: str, limit: int) -> tuple:
        path = 'v2/depth.do'
        
        params = {
        "symbol": f"{symbol}",
        "size": f"{limit}",
        }

        url = f"{APIURL}/{path}"
        return (url, params)
    
    def _format_data(self, data):
        res = {}
        res['bids'] = data['data']['bids']
        res['asks'] = data['data']['asks']
        return res 
    
    def _get_sign(self, payload):
        signature = hmac.new(self.secret_key.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
        return signature
    
    def _convert_symbols(self, symbol: str) -> str:
        return symbol.replace("/", "_").lower()
    
    async def load_symbols(self, session: aiohttp.ClientSession):
        self.listed_tokens = []

        endpoint = "v2/currencyPairs.do"

        uri = f"{APIURL}/{endpoint}"

        res = await self._send_request(uri, {}, session)

    
        for symbol in res['data']:
            m, q = symbol.split('_')
            self.listed_tokens.append(f"{m.upper()}/{q.upper()}")

    async def load_chains(self, session):
        self.chains = {}

        endpoint = "v2/withdrawConfigs.do"
        
        uri = f"{APIURL}/{endpoint}"
        
        res = await self._send_request(uri, {}, session)

        for chain in res['data']:
            if not chain.get('assetCode', False) or not chain.get('chain', False):
                continue 

            if chain['assetCode'].upper() not in self.chains:
                self.chains[chain['assetCode'].upper()] = {}

            formated_name = chains_mapping.get(chain['chain'].upper(), chain['chain'].upper())

            self.chains[chain['assetCode'].upper()][formated_name] = {
                    'deposit': chain.get('depositEnable', True),
                    'withdraw': chain.get('canWithDraw', None),
                    'withdrawFee': chain.get('fee', float('inf')),
                    'withdrawMin': chain.get('min', None),
                    'withdrawMax': chain.get('withdrawMax', None),
                    'contract': chain.get('contractAddress', None)
            }
        