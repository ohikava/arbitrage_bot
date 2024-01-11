from collections import Counter 
import logging 

ONLY_USDT = "ONLY_USDT"
ONLY_USDC = "ONLY_USDC"
ONLY_STABLECOINS = "ONLY_STABLECOINS"
ONLY_SHITCOINS = "ONLY_SHITCOINS"
ONLY_REAL_COINS = "ONLY_REAL_COINS"

filters = {
    ONLY_USDT: lambda x: 'USDT' in x,
    ONLY_USDC: lambda x: 'USDC' in x,
    ONLY_STABLECOINS: lambda x: 'USDT' in x or 'USDC' in x or 'TUSD' in x or 'BUSD' in x or 'DAI' in x or 'USDD' in x
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

        self.bl = set({
            "BTC",
            "ETH",
            'EUR'
        })
        

    def _update_tokens_list(self):
        """
        Update the list of tokens that will be used in arbitrage
        """
        self.tokens = []
        for token in self.all_tokens:
            main_coin = token.split('/')[0]
            quote_coin = token.split("/")[1]

            skip_token = False 
            for filter in self.filters:
                if not filters[filter](token) or main_coin in self.bl or quote_coin in self.bl:
                    skip_token = True
                    break
            if skip_token:
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

    def add_token_to_bl(self, token:str):
        """
        Add token to the blacklist
        """
        self.bl.add(token)

        self._update_tokens_list()

    def remove_token_from_bl(self, token:str):
        """
        Remove token from the blacklist
        """
        self.bl.remove(token)

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
    
    def update_list_of_tokens(self, markets: list):
        """
        Updates list of all available tokens
        :param markets: list of markets
        """
        
        all_tokens = sum([i.listed_tokens for i in markets], [])
        tokens_counts = Counter(all_tokens)

        all_tokens_processed = [key for key, value in tokens_counts.items() if value >= 2]

        self.all_tokens = all_tokens_processed
        logging.debug(f"Symbols have been updated. Loaded {len(self.all_tokens)} symbols")

        self._update_tokens_list()


