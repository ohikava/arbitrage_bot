import logging
import time 
import aiohttp 

class Market(object):
    def __init__(self) -> None:
        self.name = self.__class__.__name__
        self.depth = {}
        self.last_request = None 
        self.requests_num = 0
        self.TRADING_FEE = 0.1
        

    async def _send_request(self, uri: str, params: dict, session: aiohttp.ClientSession):
        """
        Sends request to the exchange
        :param uri: uri of the request
        :param params: parameters of the request
        :param session: session that will be used to send requests
        :return: response of the request
        """
        self.check_time_restrictions()

        async with session.get(uri, params=params) as response:
            if self.check_response(response):
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
        if self.requests_num > self.LIMIT and time.time() - self.last_request < self.TIME_RATE:
            time.sleep(self.TIME_RATE - time.time() + self.last_request + 1)
            self.requests_num = 0

    def check_response(self, response):
        """
        Checks the response code
        """
        if response.status == 200:
            return True 
        elif response.status == 429:
            logging.error(f"Too many requests on {self.name} market")
            raise Exception(f"Too many requests on {self.name} market")
        else:
            logging.error(f"Error. Status code on {self.name} is {response.status}")
            raise f"Error. Status code on {self.name} is {response.status}"
    
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

