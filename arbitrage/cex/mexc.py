from arbitrage.cex.market import Market
import requests
from dotenv import load_dotenv
import os
import hmac 
from hashlib import sha256
import time 

load_dotenv()

APIURL = "https://api.mexc.com"

chains_formater = {
    'BNB Smart Chain(BEP20)': 'BEP20',
    'Bitcoin(BTC)': 'BTC',
}
class MEXC(Market):
    def __init__(self) -> None:
        super().__init__()
        self.LIMIT = 20000
        self.TIME_RATE = 60
        self.api_key = os.getenv("MEXC_API_KEY")
        self.secret_key = os.getenv("MEXC_SECRET_KEY")
        self.time_stamp = str(int(time.time() * 10 ** 3))
        self.recv_window = "5000"

    def _convert_symbols(self, symbol: str) -> str:
        return symbol.replace("/", "")
    
    def get_request_info(self, symbol: str, limit: int) -> tuple:
        path = 'api/v3/depth'
        uri = f"{APIURL}/{path}"

        params = {
        "symbol": f"{symbol}",
        "limit": f"{limit}",
        }

        return (uri, params)
    
    def _get_sign(self, payload):
        signature = hmac.new(self.secret_key.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
        return signature
    
    def _format_data(self, data):
        res = {}
        res['bids'] = data['bids']
        res['asks'] = data['asks']
        return res 
    
    async def load_symbols(self, session):
        self.listed_tokens = []
        
        endpoint = "api/v3/ticker/price"

        uri = f"{APIURL}/{endpoint}"

        res = await self._send_request(uri, {}, session)

        f = []
        for symbol in res:
            symbol = symbol['symbol']
            if symbol.endswith("USDT"):
                f.append(f"{symbol[:-4]}/USDT")
            elif symbol.endswith("BTC"):
                f.append(f"{symbol[:-3]}/BTC")
            elif symbol.endswith("ETH"):
                f.append(f"{symbol[:-3]}/ETH")
            elif symbol.endswith("USDC"):
                f.append(f"{symbol[:-4]}/USDC")
            elif symbol.endswith("TUSD"):
                f.append(f"{symbol[:-4]}/TUSD")

        self.listed_tokens = f 

    async def load_chains(self, session):
        self.chains = {}

        endpoint = "/api/v3/capital/config/getall"
        
        uri = f"{APIURL}/{endpoint}"
        
        self.time_stamp = str(int(time.time() * 10 ** 3))
        payload = f"recvWindow={self.recv_window}&timestamp={self.time_stamp}"  


        signature = self._get_sign(payload)
        headers = {
           "apiKey": self.api_key,
        }

        uri = f"{uri}?{payload}&signature={signature}"
        res = await self._send_request(uri, {}, session, headers=headers)
    
        for chain in res:
            networkList = chain['networkList']
            self.chains[chain['coin']] = {
                
            }

            for network in networkList:
                formated_name = chains_formater.get(network['network'], network['network'])
                self.chains[chain['coin']][formated_name] = {
                    'deposit': network.get('depositEnable', None),
                    'withdraw': network.get('withdrawEnable', None),
                    'withdrawFee': network.get('withdrawFee', None),
                    'withdrawMin': network.get('withdrawMin', None),
                    'withdrawMax': network.get('withdrawMax', None),
                    'contract': network.get('contract', None),
                }

