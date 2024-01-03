import logging
import time 

class Market(object):
    def __init__(self) -> None:
        self.name = self.__class__.__name__
        self.depth = {}
        self.last_request = None 
        self.requests_num = 0
        
        with open(f"symbols/{self.name.lower()}.txt") as file:
            self.listed_tokens = [i.strip() for i in file.readlines()]

    
    def convert_to_usd(self):
        pass 
    
    def get_symbol_depth(self, symbol):
        return {}

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
    
    def _convert_symbols(self, symbol:str) -> str:
        """
        This function is used to convert standart symbol name to special form for a particular exchange.
        By default, returns initial symbol
        """
        return symbol
    
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
        if response.status_code == 200:
            return True 
        elif response.status_code == 429:
            logging.warn(f"Too many requests on {self.name} market")
            return False 
        else:
            raise f"Error. Status code on {self.name} is {response.status_code}"
    
    def check_symbol_listed(self, symbol: str):
        """
        Checks whether the symbol is being listed on a CEX
        """
        return symbol in self.listed_tokens
