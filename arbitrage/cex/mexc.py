from arbitrage.cex.market import Market
import requests


APIURL = "https://api.mexc.com"
class MEXC(Market):
    def __init__(self) -> None:
        super().__init__()
        self.LIMIT = 20000
        self.TIME_RATE = 60

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


