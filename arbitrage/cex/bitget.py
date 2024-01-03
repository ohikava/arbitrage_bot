from arbitrage.cex.market import Market
import aiohttp
import time

APIURL = "https://api.bitget.com"
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
        
    
    # async def get_symbol_depth(self, symbol: str, session:aiohttp.ClientSession, limit: int = 5) -> dict:
    #     path = 'api/v2/spot/market/orderbook'
        
    #     symbol = self._convert_symbols(symbol)

    #     method = "GET"
    #     params = {
    #     "symbol": f"{symbol}",
    #     "limit": f"{limit}",
    #     "type": "step0"
    #     }

    #     url = f"{APIURL}/{path}"

    #     res_json = await self._send_request(url, params, session)
    #     self.last_request = time.time()
    #     self.requests_num += 1
        
    #     if res_json:
    #         res = self._format_data(res_json)
    #         return res
    #     return None 
    
    def _convert_symbols(self, symbol: str) -> str:
        return symbol.replace("/", "")

