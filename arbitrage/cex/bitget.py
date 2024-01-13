from arbitrage.cex.market import Market
import aiohttp
import time

APIURL = "https://api.bitget.com"

chains_formater = {
}

class BitGet(Market):
    def __init__(self) -> None:
        super().__init__()
        self.LIMIT = 10
        self.TIME_RATE = 1
    
    def get_request_info(self, symbol: str, limit: int) -> tuple:
        path = 'api/v2/spot/market/orderbook'
        
        params = {
        "symbol": f"{symbol}",
        "limit": f"{limit}",
        "type": "step0"
        }

        url = f"{APIURL}/{path}"
        return (url, params)
        
    def _convert_symbols(self, symbol: str) -> str:
        return symbol.replace("/", "")
    
    async def load_symbols(self, session: aiohttp.ClientSession):
        self.listed_tokens = []

        endpoint = "api/v2/spot/public/symbols"

        uri = f"{APIURL}/{endpoint}"

        res = await self._send_request(uri, {}, session)

        self.requests_num += 1
        self.last_request = time.time()

        for symbol in res['data']:
            self.listed_tokens.append(f"{symbol['baseCoin']}/{symbol['quoteCoin']}")

    async def load_chains(self, session: aiohttp.ClientSession):
        self.chains = {}

        endpoint = "api/spot/v1/public/currencies"

        uri = f"{APIURL}/{endpoint}"

        res = await self._send_request(uri, {}, session)

        self.requests_num += 1
        self.last_request = time.time()

        for chain in res['data']:
            networkList = chain['chains']
            self.chains[chain['coinName']] = dict()

            for network in networkList:
                formated_name = chains_formater.get(network['chain'], network['chain'])
                self.chains[chain['coinName']][formated_name] = {
                    'deposit': bool(network.get('rechargeable', None)),
                    'withdraw': bool(network.get('withdrawable', None)),
                    'withdrawFee': network.get('withdrawFee', None),
                    'withdrawMin': network.get('minWithdrawAmount', None),
                    'withdrawMax': network.get('withdrawMax', None),
                    'contract': network.get('contract', None),
                }
