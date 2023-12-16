from arbitrage import config 
import json 

class ArbitrageBot:
    def __init__(self) -> None:
        self.markets = []
        self.observers = []
        self.depths = {} 

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
        self.load_pair_depth('BTCUSDT') 

        with open("all_data.json", 'w') as file:
            json.dump(self.depths, file)


    


