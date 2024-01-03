import copy

ONLY_USDT = "ONLY_USDT"
ONLY_USDC = "ONLY_USDC"
ONLY_STABLECOINS = "ONLY_STABLECOINS"
ONLY_SHITCOINS = "ONLY_SHITCOINS"
ONLY_REAL_COINS = "ONLY_REAL_COINS"

filters = {
    ONLY_USDT: lambda x: 'USDT' in x,
    ONLY_USDC: lambda x: 'USDC' in x,
    ONLY_STABLECOINS: lambda x: 'USDT' in x or 'USDC' in x
}

class Tokens:
    def __init__(self):
        """
        This class has 2 purposes
        1. Provide a list of tokens to be used in the arbitrage bot
        2. Provide a way to filter out tokens that are not supported by the exchanges
        """
        self.filters = set()
        self.all_tokens = ['BTC/USDT']
        self.limit = None 

        with open("symbols/all.txt", "r") as file:
            self.all_tokens = [i.strip() for i in file.read().splitlines()]

        
        self._update_tokens_list()
        

    def _update_tokens_list(self):
        """
        Update the list of tokens that will be used in arbitrage
        """
        self.tokens = []
        for token in self.all_tokens:
            for filter in self.filters:
                if not filters[filter](token):
                    continue 
            self.tokens.append(token)

        if self.limit:
            self.tokens = self.tokens[:self.limit]


    def set_filter(self, filter:str):
        """
        Used to set filters for the tokens
        Available options:
        - ONLY_USDT
        - ONLY_USDC
        - ONLY_STABLECOINS
        """

        if filter not in self.filters:
            self.filters.add(filter)

        self._update_tokens_list()

    def remove_filter(self, filter:str):
        """
        Remove a filter from the list of filters
        """
        self.filters.remove(filter)

        self._update_tokens_list()
    
    def set_limit(self, limit:int):
        """
        Set limit for the amount of tokens to be used in arbitrage
        """
        self.limit = limit
        self._update_tokens_list()
    
    def __iter__(self):
        return iter(self.tokens)
