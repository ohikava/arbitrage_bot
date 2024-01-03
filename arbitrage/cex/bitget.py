from arbitrage.cex.market import Market
import aiohttp

APIURL = "https://api.bitget.com"
class BitGet(Market):
    def __init__(self) -> None:
        super().__init__()
        self.LIMIT = 10
        self.TIME_RATE = 1

    async def _send_request(self, endpoint, params):

        self.check_time_restrictions()

        url = f"{APIURL}/{endpoint}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params) as response:
                res = await response 

                if self.check_response(res):
                    return res.json()
    
    async def get_symbol_depth(self, symbol: str, limit: int = 5) -> float:
        path = 'api/v2/spot/market/orderbook'
        
        symbol = self._convert_symbols(symbol)

        method = "GET"
        params = {
        "symbol": f"{symbol}",
        "limit": f"{limit}",
        "type": "step0"
        }

        res_json = await self._send_request(method, path, params)

        if res_json:
            res = self._format_data(res_json)
            return res
        return None 
    
    def _convert_symbols(self, symbol: str) -> str:
        return symbol.replace("/", "")

