from arbitrage.cex.market import Market
import os 
import requests
import hmac 
from hashlib import sha256
from dotenv import load_dotenv
import time 
import json 

load_dotenv()

APIURL = "https://open-api.bingx.com"

symbols_mapping = {
    "BTCUSDT": 'BTC-USDT'
}


class BingX(Market):
    def __init__(self) -> None:
        super().__init__()
        self.api_key = os.getenv("BINGX_API_KEY")
        self.secret_key = os.getenv("BINGX_SECRET_KEY")

    def _get_sign(self, payload):
        signature = hmac.new(self.secret_key.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
        print("sign=" + signature)
        return signature


    def _send_request(self, method, path, urlpa, payload):
        url = "%s%s?%s&signature=%s" % (APIURL, path, urlpa, self._get_sign(urlpa))
        print(url)
        headers = {
            'X-BX-APIKEY': self.api_key,
        }
        response = requests.request(method, url, headers=headers, data=payload)
        
        return response.json()

    def _params2str(self, paramsMap:dict):
        sortedKeys = sorted(paramsMap)
        paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
        return paramsStr+"&timestamp="+str(int(time.time() * 1000))

    def get_symbol_depth(self, symbol: str) -> float:
        payload = {}
        path = '/openApi/swap/v2/quote/depth'
        method = "GET"
        params = {
        "symbol": symbols_mapping[symbol],
        "limit": "100"
        }
        params_str = self._params2str(params)
        
        res_json = self._send_request(method, path, params_str, payload)

        res = self._format_data(res_json)

        return res
    
    def _format_data(self, data):
        res = {}
        res['bids'] = data['data']['bids']
        res['asks'] = data['data']['asks']
        return res 
    


if __name__ == "__main__":
    bingx = BingX()
    print(bingx.get_token_price('BTCUSDT'))
