import requests 
import os 
from dotenv import load_dotenv
import time 
import hmac
import hashlib
from arbitrage.cex.market import Market

load_dotenv()  


url = "https://api.bybit.com"
api_key=os.getenv('BYBIT_API_KEY')
secret_key=os.getenv('BYBIT_API_SECRET')

httpClient=requests.Session()
recv_window=str(10000)

class ByBit(Market):
    def __init__(self) -> None:
        pass
    
    def _http_request(self, endPoint,method,payload,Info):
        global time_stamp
        time_stamp=str(int(time.time() * 10 ** 3))
        signature=self._get_signature(payload)

        headers = {
            'X-BAPI-API-KEY': api_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-SIGN-TYPE': '2',
            'X-BAPI-TIMESTAMP': time_stamp,
            'X-BAPI-RECV-WINDOW': recv_window,
            'Content-Type': 'application/json'
        }
        if(method=="POST"):
            response = httpClient.request(method, url+endPoint, headers=headers, data=payload)
        else:
            response = httpClient.request(method, url+endPoint+"?"+payload, headers=headers)
        print(response.text)
        print(Info + " Elapsed Time : " + str(response.elapsed))

    def _get_signature(self, payload):
        param_str= str(time_stamp) + api_key + recv_window + payload
        hash = hmac.new(bytes(secret_key, "utf-8"), param_str.encode("utf-8"),hashlib.sha256)
        signature = hash.hexdigest()
        return signature

    def get_unfilled_orders(self, basecoin, settlecoin):
        endpoint = "/v5/order/realtime"
        method = 'GET'
        params=f'category=spot&symbol={basecoin}{settlecoin}'
        self._http_request(endpoint, method, params, 'UnFilled')


if __name__ == "__main__":
    bybit = Bybit()
    bybit.get_unfilled_orders(basecoin='BTC', settlecoin='USDT')



