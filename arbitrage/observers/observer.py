import abc


class Observer(object, metaclass=abc.ABCMeta):
    def start_search(self, depths):
        pass

    def end_search(self):
        pass

    @abc.abstractmethod
    def opportunity(
        self,
        bid:str,
        ask:str,
        bid_price:str,
        ask_price:str,
        spread:str,
        liquidity:str,
        symbol:str
    ):
        """
        Function that will be called for every arbitrage opportunity found
        :param bid: name of the exchange with the highest bid
        :param ask: name of the exchange with the lowest ask
        :param bid_price: highest bid price
        :param ask_price: lowest ask price
        :param spread: spread value
        :param liquidity: liquidity value
        :param symbol: symbol of the pair
        """
        pass
