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

    def init_markets(self, markets_list):
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

    def init_observers(self, observers_list):
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
    
    def load_pair_depth(self, pair):
        self.depths[pair] = {}
        
        for market in self.markets:
            self.depths[pair][market.name] = market.get_symbol_depth(pair)
        

    def watch(self, args):
        for token in self.tokens:
            self.load_pair_depth(token)
        
        with open("all_data.json", 'w') as file:
            json.dump(self.depths, file)
        
    def _find_spread_by_two_cex(self, cex1_info, cex2_info, spread_limit=0.05):
        bids1 = [float(i[0]) for i in cex1_info['bids']]
        bids2 = [float(i[0]) for i in cex2_info['bids']]

        asks1 = [float(i[0]) for i in cex1_info['asks']]
        asks2 = [float(i[0]) for i in cex2_info['asks']]

        spread1 = bids1[0] / asks2[0] - 1
        if bids1[0] > asks2[0] and spread1 > spread_limit:
            return ('bids', 'asks')
        
        spread2 = bids2[0] / asks1[0] - 1
        if bids2[0] > asks1[0] and spread2 > spread_limit:
            return ('asks', 'bids')

        return (None, None)

    def find_spread(self, data):
        map_ba = {
        'asks': 'buy',
        'bids': 'sell'
        }

        for cex1 in data:
            for cex2 in data:
                if cex1 == cex2:
                    continue 
                
                cex1_info = data[cex1]
                cex2_info = data[cex2]
                scan = self._find_spread_by_two_cex(cex1_info, cex2_info)

                if scan[0]:
                    price1 = float(cex1_info[scan[0]][0][0])
                    price2 = float(cex2_info[scan[1]][0][0])

                    spread = max(price1, price2)/min(price1, price2)-1
                    print(f"CEX 1: {map_ba[scan[0]]}, CEX 2: {map_ba[scan[1]]}. Price 1: {price1}, Price 2: {price2}. Spread: {spread}%")



    


