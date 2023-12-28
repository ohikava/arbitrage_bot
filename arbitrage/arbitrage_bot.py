from arbitrage import config 
import json 
from arbitrage.tokens import Tokens

class ArbitrageBot:
    def __init__(self) -> None:
        self.markets = []
        self.observers = []
        self.depths = {} 
        self.tokens = Tokens()

        self.init_markets(config.markets)
        self.init_observers(config.observers)

        self.spread_limit = 0.05
    
    def _load_pair_depth(self, pair):
        self.depths[pair] = {}
        
        for market in self.markets:
            self.depths[pair][market.name] = market.get_symbol_depth(pair)
        
    def _find_spread_by_two_cex(self, cex1:str, cex1_info:dict, cex2:str, cex2_info:dict) -> dict | None:
        """
        Function finds spread by two cex 
        :param cex1: this is name of cex1
        :param cex1_info: this is a dictionary with bids and asks from cex1
        :param cex2: this is name of cex2
        :param cex2_info: this is a dictionary with bids and asks from cex2
        :returns: tuple with spread info or None. Tuple looks like this: (bid, ask, bid_price, ask_price, spread, liquidity)
        """
        bids_cex1 = [float(i[0]) for i in cex1_info['bids']]
        bids_cex2 = [float(i[0]) for i in cex2_info['bids']]

        asks_cex1 = [float(i[0]) for i in cex1_info['asks']]
        asks_cex2 = [float(i[0]) for i in cex2_info['asks']]

        

        spread1 = (bids_cex1[0] - asks_cex2[0]) / asks_cex2[0]
        if spread1 > self.spread_limit:
            liquidity = min(float(cex1_info['bids'][0][1]), float(cex2_info['asks'][0][1]))

            return (cex1, cex2, cex1_info['bids'][0][0], cex2_info['asks'][0][0], str(spread1), str(liquidity))
        
        spread2 = (bids_cex2[0] - asks_cex1[0]) / asks_cex1[0]
        if spread2 > self.spread_limit:
            liquidity = min(float(cex1_info['asks'][0][1]), float(cex2_info['bids'][0][1]))

            return (cex2, cex1, cex2_info['bids'][0][0], cex1_info['asks'][0][0], str(spread2), str(liquidity))
        
        return None


    def init_markets(self, markets_list: list):
        """
        Function initializes markets modules
        :param markets_list: list of markets names that will be used in arbitrage
        """
        self.markets_names = markets_list
        for market_name in markets_list:
            try:
                exec("import arbitrage.cex." + market_name.lower())
                market = eval(
                    "arbitrage.cex." + market_name.lower() + "." + market_name + "()"
                )

                self.markets.append(market)

            except (ImportError, AttributeError) as e:
                print(
                    "%s market name is invalid: Ignored (you should check your config file)"
                    % (market_name)
                ) 

    def init_observers(self, observers_list: list):
        """
        Function initializes observers modules that will sent notifications about occuring spreads to user
        :param observers_list: list of observers names that will be used in arbitrage
        """
        self.observer_names = observers_list
        for observer_name in observers_list:
            try:
                exec("import arbitrage.observers." + observer_name.lower())
                observer = eval(
                    "arbitrage.observers." + observer_name.lower() + "." + observer_name + "()"
                )

                self.observers.append(observer)
                
            except (ImportError, AttributeError) as e:
                print(
                    "%s observer name is invalid: Ignored (you should check your config file)"
                    % (observer_name)
                )

    def watch(self, args:dict):
        """
        Function start watching for arbitrage opportunities in infinite loop
        :param args: arguments of the arbitrage
        """
        pass 
        
    def scan(self):
        """
        Function loads current depth from all markets and looks for arbitrage opportunities
        """
        # for token in self.tokens:
        #     self._load_pair_depth(token)
        
        with open("tests/fake_spreads.json", 'r') as file:
            depths = json.load(file)
        


        spreads = self.find_spread(depths)

        for opportunity in spreads:
            for observer in self.observers:
                observer.opportunity(*opportunity)

    def find_spread(self, depth):
        """
        Function searches for arbitrage opportunities given the depths
        :param data: dictionary with depths from all markets. Example of data: {"BTC/USDT": {"Bybit": {"bids": [["10", "1]], "asks": [["11", "1"]]}}}
        """
        spreads = []

        for symbol in depth:
            symbol_data = depth[symbol]
            cex_pairs = set()

            for cex1 in symbol_data:
                for cex2 in symbol_data:
                    if cex1 == cex2 or (cex1, cex2) in cex_pairs or (cex2, cex1) in cex_pairs:
                        continue 
                    
                    cex1_info = symbol_data[cex1]
                    cex2_info = symbol_data[cex2]
                    
                    scan = self._find_spread_by_two_cex(cex1, cex1_info, cex2, cex2_info)

                    if scan:
                        spreads.append(tuple(
                            list(scan) + [symbol]
                        ))

                    cex_pairs.add((cex1, cex2))

        return spreads
    
    
