import logging

class Market(object):
    def __init__(self) -> None:
        self.name = self.__class__.__name__
        self.update_rate = 60
    
    def convert_to_usd(self):
        pass 
    
    def update_depth(self):
        pass 
    