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

