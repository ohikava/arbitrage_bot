import copy

FILTERS = {
    'only_usdt': lambda token: 'USDT' in token.split('/'),
}

class Tokens:
    def __init__(self):
        """
        This class has 2 purposes
        1. Provide a list of tokens to be used in the arbitrage bot
        2. Provide a way to filter out tokens that are not supported by the exchanges
        """
        self.filters = []
        self.all_tokens = ['BTC/USDT']
        self.limit = None 

        with open("symbols/bybit.txt", "r") as file:
            self.all_tokens = [i.strip() for i in file.read().splitlines()]

        
        self._update_tokens_list()
        

    def _update_tokens_list(self):
        """
        Update the list of tokens that will be used in arbitrage
        """
        self.tokens = []
        for filter in self.filters:
            for token in self.all_tokens:
                if FILTERS[filter](token):
                    self.tokens.append(token)

        if len(self.filters) == 0:
            self.tokens = copy.copy(self.all_tokens)
        if self.limit:
            self.tokens = self.tokens[:self.limit]

    def set_filter(self, filter):
        """
        Used to set filters for the tokens
        Available options:
        - only_usdt
        """

        if filter not in self.filters:
            self.filters.append(filter)

        self._update_tokens_list()
    
    def set_limit(self, limit:int):
        """
        Set limi for the amount of tokens to be used in arbitrage
        """
        self.limit = limit
        self._update_tokens_list()
        
    def remove_filter(self, filter:str):
        """
        Remove a filter from the list of filters
        """
        self.filters.remove(filter)

        self._update_tokens_list()

    def load_available_tokens(self, exchanges:list):
        """
        Load all tokens available on the exchanges
        """
        self.exchanges_tokens = {}
        for exchange in exchanges:
            self.exchanges_tokens[exchange] = exchange.get_available_tokens()

    
    def filter(self, exchange:str, symbol:str) -> bool:
        """
        Return True if the symbol is available on the exchange
        """
        return symbol in self.exchanges_tokens[exchange] 
    
    def __iter__(self):
        return iter(self.tokens)
