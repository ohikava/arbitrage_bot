import abc


class Observer(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def opportunity(
        self,
        cex_bid:str,
        cex_ask:str,
        bid_price:str,
        ask_price:str,
        spread:str,
        bid_liquidity:str,
        ask_liquidity:str,
        symbols:str,
        chains: list,
        withdraw_fee: float,
        ask_trade_fee: float,
        bid_trade_fee: float,
    ):

        """
        Function that will be called for every arbitrage opportunity found
        :param cex_bid: cex where we are selling
        :param cex_ask: cex where we are buying
        :param bid_price: highest bid price
        :param ask_price: lowest ask price
        :param spread: spread value
        :param bid_liquidity: liquidity of the highest bid
        :param ask_liquidity: liquidity of the lowest ask
        :param symbol: symbol of the pair
        :param chains: available chains for the symbol
        :param withdraw_fee: withdraw fee for the symbol (in the main coin )
        :param ask_trade_fee: ask trade fee
        :param bid_trade_fee: bid trade fee
        """
        pass
