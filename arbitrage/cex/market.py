import logging
import time 
import aiohttp 
import hmac 
from hashlib import sha256
from collections import deque

class Market(object):
    def __init__(self) -> None:
        self.name = self.__class__.__name__
        self.depth = {}
        self.last_request = None 
        self.requests_num = 0
        self.TRADING_FEE = 0.1

        self.batch_transactions = deque()
        self.LIMIT = 10
        self.TIME_RATE = 1
        

    def manage_time_restriction(self):
        """
        This function is used to follow markets rules on number of requests 
        """
        current_time = time.time()
        if len(self.batch_transactions) < self.LIMIT:
            self.batch_transactions.append(current_time)
            return 
        
        if current_time - self.batch_transactions[0] < self.TIME_RATE: 
            pause_time = self.TIME_RATE - current_time + self.batch_transactions[0] 
            logging.debug(f"pausa for {pause_time} for {self.name} cex")
            time.sleep(pause_time)
            current_time = time.time()

        self.batch_transactions.popleft()
        self.batch_transactions.append(current_time)

    async def _send_request(self, uri: str, params: dict, session: aiohttp.ClientSession, headers: dict = {}):
        """
        Sends request to the exchange
        :param uri: uri of the request
        :param params: parameters of the request
        :param session: session that will be used to send requests
        :return: response of the request
        """
        self.manage_time_restriction()

        if headers:
            async with session.get(uri, headers=headers, data={}) as response:
                msg = await response.text()
                if self.check_response(response, msg):
                    return await response.json() 
        else:
            async with session.get(uri, params=params) as response:
                msg = await response.text()
                if self.check_response(response, msg):
                    return await response.json()
                

    async def get_symbol_depth(self, symbol: str, session: aiohttp.ClientSession, limit: int = 5) -> dict:
        """
        Returns the depth of the symbol 
        :param symbol: it is the symbol
        :param session: session that will be used to send requests
        :param limit: number of orders in the depth
        :return: dict with bids and asks
        """

        symbol = self._convert_symbols(symbol)
        url, params = self.get_request_info(symbol, limit)


        res_json = await self._send_request(url, params, session)
        self.last_request = time.time()
        self.requests_num += 1
        
        if res_json:
            res = self._format_data(res_json)
            return res
        return None 
    
    def _format_data(self, data):
        res = {}
        res['bids'] = data['data']['bids']
        res['asks'] = data['data']['asks']
        return res 
    
    def get_available_tokens(self):
        with open(f'symbols/{self.name}.txt') as file:
            data = file.readlines()
        data = [i.strip() for i in data]
        return set(data)
    
    def check_time_restrictions(self):
        """
        This function is used to follow markets rules on number of requests
        """
        if self.requests_num >= self.LIMIT and time.time() - self.last_request <= self.TIME_RATE:
            pause_time = self.TIME_RATE - time.time() + self.last_request + 1
            logging.debug(f"pausa for {pause_time} for {self.name} cex")
            time.sleep(pause_time)
            self.requests_num = 0

    def check_response(self, response, msg):
        """
        Checks the response code
        """
        if response.status == 200:
            return True 
        elif response.status == 429:
            logging.error(f"Too many requests on {self.name} market")
            raise Exception(f"Too many requests on {self.name} market")
        else:
            logging.error(f"Error. Status code on {self.name} is {response.status}. msg: {msg}")
            raise Exception(f"Error. Status code on {self.name} is {response.status}. msg: {msg}")
    
    def check_symbol_listed(self, symbol: str):
        """
        Checks whether the symbol is being listed on a CEX
        """
        return symbol in self.listed_tokens
    
    def get_request_info(self, symbol: str, limit: int) -> tuple:
        """
        Returns all information that is needed to send a request
        :return: (uri, params)
        """
        return (None, None)
    
    def _convert_symbols(self, symbol:str) -> str:
        """
        This function is used to convert standart symbol name to special form for a particular exchange.
        By default, returns initial symbol
        """
        return symbol
    
    async def load_symbols(self, session: aiohttp.ClientSession):
        """
        This function is used to load all avaialable symbols from the exchange
        :param session: session that will be used to send requests
        """
        pass

    async def load_chains(self, session: aiohttp.ClientSession):
        """
        This function is used to load information about fees, withdraw ability and other information about tokens
        :param session: session that will be used to send requests
        """
        pass

    def _get_sign(self, payload):
        signature = hmac.new(self.secret_key.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
        return signature
    
    def _praseParam(self, paramsMap):
        sortedKeys = sorted(paramsMap)
        paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
        return paramsStr+"&timestamp="+str(int(time.time() * 1000))