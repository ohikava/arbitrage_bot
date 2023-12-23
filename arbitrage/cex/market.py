import logging

class Market(object):
    def __init__(self) -> None:
        self.name = self.__class__.__name__
        self.depth = {}
        self.last_request = None 
        self.requests_num = 0

    
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