import logging

class Market(object):
    def __init__(self) -> None:
        self.name = self.__class__.__name__
        self.depth = {}
    
    def convert_to_usd(self):
        pass 
    
    def get_symbol_depth(self, symbol):
        return {}

    def _format_data(self, data):
        res = {}
        res['bids'] = data['data']['bids']
        res['asks'] = data['data']['asks']
        return res 
    