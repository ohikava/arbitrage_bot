from arbitrage.cex.market import Market
import requests

APIURL = "https://api.bitget.com"

class BitGet(Market):
    def _send_request(self, method, endpoint, params):
        url = f"{APIURL}/{endpoint}"
  
        response = requests.request(method, url, params=params)
        
        return response.json()
    
    def get_symbol_depth(self, symbol: str) -> float:
        path = '/api/spot/v1/market/depth'

        method = "GET"
        params = {
        "symbol": f"{symbol}_SPBL",
        "limit": "100",
        "type": "step0"
        }

        res_json = self._send_request(method, path, params)
        res = self._format_data(res_json)

        return res

