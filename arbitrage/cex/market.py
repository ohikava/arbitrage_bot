import logging

class Market(object):
    def __init__(self) -> None:
        self.name = self.__class__.__name__
        self.depth = {}
    
    def convert_to_usd(self):
        pass 
    
    def get_symbol_depth(self, symbol):
        return {}
    