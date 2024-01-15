from arbitrage.cex.market import Market
from arbitrage.utils.chains_mapper import chains_mapping
import aiohttp
import time
import hmac 
from hashlib import sha256
import os 
from dotenv import load_dotenv

load_dotenv()

APIURL = "https://api.binance.com"

class Binance(Market):
    def __init__(self) -> None:
        super().__init__()
        self.LIMIT = 600
        self.TIME_RATE = 60
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.secret_key = os.getenv("BINANCE_SECRET_KEY")
        self.time_stamp = str(int(time.time() * 10 ** 3))
        self.recv_window = "5000"
    
    def get_request_info(self, symbol: str, limit: int) -> tuple:
        path = 'api/v3/depth'
        
        params = {
        "symbol": f"{symbol}",
        "limit": f"{limit}",
        }

        url = f"{APIURL}/{path}"
        return (url, params)
    
    def _format_data(self, data):
        res = {}
        res['bids'] = data['bids']
        res['asks'] = data['asks']
        return res 
    
    def _get_sign(self, payload):
        signature = hmac.new(self.secret_key.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
        return signature
    
    def _convert_symbols(self, symbol: str) -> str:
        return symbol.replace("/", "")
    
    async def load_symbols(self, session: aiohttp.ClientSession):
        self.listed_tokens = []

        endpoint = "api/v3/ticker/bookTicker"

        uri = f"{APIURL}/{endpoint}"

        res = await self._send_request(uri, {}, session)

        know_tickers = ['USDT', 'DUSDT', 'USDC', 'BTC', 'ETH', 'TUSD', 'BUSD', 'AEUR', 'BNB', 'PAX', 'XRP', 'USDS', 'TRX', 'NGN', 'RUB', 'TRY', 'EUR', 'ZAR', \
                'BKRW', 'IDRT', 'GBP', 'UAH', 'BIDR', 'AUD', 'DAI', 'BRL', 'BVND', 'VAI', 'USDP', 'UST', 'PLN', 'RON', 'ARS', 'FDUSD', 'DOGE', 'DOT']

        a = []
        for s in res:
            for i in know_tickers:
                if s['symbol'].endswith(i):
                    m = s['symbol'].split(i)[0]
                    q = i 

                    a.append(f"{m}/{q}")
            
        self.listed_tokens = a 

    async def load_chains(self, session):
        self.chains = {}

        endpoint = "sapi/v1/capital/config/getall"
        
        uri = f"{APIURL}/{endpoint}"
        
        self.time_stamp = str(int(time.time() * 10 ** 3))
        payload = f"recvWindow={self.recv_window}&timestamp={self.time_stamp}"  


        signature = self._get_sign(payload)
        headers = {
           "X-MBX-APIKEY": self.api_key,
        }

        uri = f"{uri}?{payload}&signature={signature}"
        res = await self._send_request(uri, {}, session, headers=headers)

        for chain in res:
            networkList = chain['networkList']
            self.chains[chain['coin']] = {
                
            }

            for network in networkList:
                formated_name = chains_mapping.get(network['network'], network['network'])
                self.chains[chain['coin']][formated_name] = {
                    'deposit': network.get('depositEnable', None),
                    'withdraw': network.get('withdrawEnable', None),
                    'withdrawFee': network.get('withdrawFee', None),
                    'withdrawMin': network.get('withdrawMin', None),
                    'withdrawMax': network.get('withdrawMax', None),
                    'contract': network.get('contractAddress', None)
                }