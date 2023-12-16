from arbitrage.cex.market import Market
import requests


APIURL = "https://api.mexc.com"
class MEXC(Market):
    def _send_request(self, method, endpoint, params):
        url = f"{APIURL}/{endpoint}"
  
        response = requests.request(method, url, params=params)
        
        return response.json()
    
    def get_symbol_depth(self, symbol: str) -> float:
        path = '/api/v3/depth'

        method = "GET"
        params = {
        "symbol": f"{symbol}",
        "limit": "100",
        }

        res_json = self._send_request(method, path, params)
        res = self._format_data(res_json)

        return res
    
    def _format_data(self, data):
        res = {}
        res['bids'] = data['bids']
        res['asks'] = data['asks']
        return res 

