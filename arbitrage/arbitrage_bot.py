from arbitrage import config 
from arbitrage.tokens import Tokens, ONLY_STABLECOINS
from arbitrage.utils.chains_mapper import chains_mapping
import logging
import time 
from datetime import datetime 
import asyncio 
import aiohttp
import json 

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.DEBUG, filename=f"logs/{datetime.today().strftime('%Y-%m-%d')}.txt", filemode='w')

logging.getLogger("asyncio").setLevel(logging.WARNING)

class ArbitrageBot:
    def __init__(self) -> None:
        self.markets = {}
        self.observers = []
        self.depths = {} 
        self.tokens = Tokens()
        self.tokens.set_filter(ONLY_STABLECOINS)
        self.tokens.set_limit(100)

        self.init_markets(config.markets)
        self.init_observers(config.observers)

        self.spread_limit = 0.05
        self.symbols_update_interval = 60 * 60 * 2   
        self.chains_update_interval = 60 * 60 * 1

    async def _get_depths(self, pair):
        self.depths[pair] = {}
        tasks = []
        tasks_names = []

        async with aiohttp.ClientSession() as session:
            for market in self.markets.values():
                if not market.check_symbol_listed(pair):
                    continue 

                task =  market.get_symbol_depth(pair, session)
                tasks.append(task)
                tasks_names.append(market.name)
                
                
            responses = await asyncio.gather(*tasks, return_exceptions=True)

            for i in range(len(responses)):
                market = tasks_names[i]
                depth = responses[i]

                if type(depth) is not dict:
                    logging.error(f"{market} market has returned invalid response: {depth.__class__.__name__} {depth}")

                self.depths[pair][market] = depth
        
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
            return (cex1, cex2, cex1_info['bids'][0][0], cex2_info['asks'][0][0], str(spread1), cex1_info['bids'][0][1], cex2_info['asks'][0][1])
        
        spread2 = (bids_cex2[0] - asks_cex1[0]) / asks_cex1[0]
        if spread2 > self.spread_limit:
            return (cex2, cex1, cex2_info['bids'][0][0], cex1_info['asks'][0][0], str(spread2), cex2_info['bids'][0][1], cex1_info['asks'][0][1])
        
        return None


    def init_markets(self, markets_list: list):
        """
        Function initializes markets modules
        :param markets_list: list of markets names that will be used in arbitrage
        """
        for market_name in markets_list:
            try:
                exec("import arbitrage.cex." + market_name.lower())
                market = eval(
                    "arbitrage.cex." + market_name.lower() + "." + market_name + "()"
                )

                self.markets[market_name] = market

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
        i = 1

        self.last_symbols_update = None # Initialistion
        self.last_chains_update = None # Initialistion

        while True:
            logging.debug(f"Iteration #{i} has started")
            self.update_symbols()
            self.update_chains()


            # Commented code below is used to get all available chains for every token in order to find out chains that has different names on different markets
            # a = {}
            # for symbol in self.tokens:
            #     token = symbol.split("/")[0]
            #     a[token] = []
            #     for m in self.markets.values():
            #         if m.check_symbol_listed(symbol) and token in m.chains:
            #             for chain in m.chains[token]:
            #                 a[token].append(chains_mapping.get(chain, chain))  
            #     a[token] = list(set(a[token]))
            # with open("logs/chains.json", "w") as file:
            #     json.dump(a, file, indent=4)
            # b = {j for i in a.values() for j in i}
            # with open("logs/available_chains.json", "w") as file:
            #     json.dump(list(b), file, indent=4)
            

            # t_s = time.time()
            # self.scan()
            # t_e = time.time()

            # logging.debug(f"Iteration #{i} has ended. It took {t_e - t_s} seconds")

            time.sleep(config.refresh_rate)
            i += 1
    
    def update_chains(self):
        """
        Function updates chains for every market
        """
        if not self.last_chains_update or time.time() - self.last_chains_update > self.chains_update_interval:
            asyncio.run(self._load_available_chains())
            
            self.last_chains_update = time.time()

    async def _load_available_chains(self):
        """
        Function loads available chains for every market
        """
        tasks = []
        async with aiohttp.ClientSession() as session:
            for market in self.markets.values():

                task =  market.load_chains(session)
                tasks.append(task)
                
                
            responses = await asyncio.gather(*tasks, return_exceptions=True) 

        for market_name, response in zip(self.markets, responses):
            if not (response is None):
                logging.error(f"{response.__class__.__name__}: {response} on {market_name} market during chains loading")
                raise Exception(f"{response.__class__.__name__}: {response} on {market_name} market during chains loading")
            
    async def _load_available_symbols(self):
        """
        Function loads available symbols for every market
        """
        tasks = []
        async with aiohttp.ClientSession() as session:
            for market in self.markets.values():

                task =  market.load_symbols(session)
                tasks.append(task)
                
                
            responses = await asyncio.gather(*tasks, return_exceptions=True) 

        for market_name, response in zip(self.markets, responses):
            if not (response is None):
                logging.error(f"{response.__class__.__name__}: {response} on {market_name} market during symbols loading")
                raise Exception(f"{response.__class__.__name__}: {response} on {market_name} market during symbols loading")
            
    def update_symbols(self):
        """
        Runs _load_available_symbols with particular interval
        """
        if not self.last_symbols_update or time.time() - self.last_symbols_update > self.symbols_update_interval:
                asyncio.run(self._load_available_symbols())
                self.last_symbols_update = time.time()
                
                self.tokens.update_list_of_tokens(self.markets.values())


    
    def filter_oppotunities(self, opportunities:list):
        """
        Function filters opportunities by addtional conditions and add some extra info
        :param opportunities: list of opportunities
        :returns: list of filtered opportunities
        """
        pass 

    def scan(self):
        """
        Function loads current depth from all markets and looks for arbitrage opportunities
        """
        for symbol in self.tokens:
            asyncio.run(self._get_depths(symbol))
        
        logging.debug(f"Depths have been loaded. Loaded {len(self.depths)} depths")
        
        # with open("tests/fake_spreads.json") as file:
        #     self.depths = json.load(file)
        
        spreads = self.find_spread(self.depths)
        logging.debug(f"Spreads have been found. Found {len(spreads)} spreads")

        for opportunity in spreads:
            for observer in self.observers:
                observer.opportunity(*opportunity)

        # print(self.depths)

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
    
    
