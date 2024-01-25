from arbitrage import config 
from arbitrage.tokens import Tokens, ONLY_STABLECOINS
from arbitrage.utils.chains_mapper import chains_mapping
from arbitrage.utils.funcs import find_dicts_intersection, find_optimal_spread, get_spread, calculate_liquidity
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
        self.tokens.set_limit(200)

        self.init_markets(config.markets)
        self.init_observers(config.observers)

        self.spread_limit = 0.01
        self.symbols_update_interval = 60 * 60 * 2   
        self.chains_update_interval = 60 * 60 * 1


        self.spreads_buffer = set()
        self.buffer_update_interval = 60 * 60 * 1

        self.liquidity_limit = 30

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
        
    def _find_spread_by_two_cex(self, symbol: str, cex1:str, cex1_info:dict, cex2:str, cex2_info:dict) -> dict | None:
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
        
        try:
            spread1 = (bids_cex1[0] - asks_cex2[0]) / asks_cex2[0]
        except:
            return None 
        if spread1 >= self.spread_limit:
            if spread1 >= 0.15:
                p1, p2, spread, liquidity = find_optimal_spread(cex2_info['asks'], cex1_info['bids'])
                
                bid_liquidity = calculate_liquidity(cex1_info['bids'][:p2+1])
                ask_liquidity = calculate_liquidity(cex2_info['asks'][:p1+1])

                if min(bid_liquidity, ask_liquidity) < self.liquidity_limit:
                    logging.debug(f"{symbol} {cex2}->{cex1} was reject because liquidity is too low")
                    return None
            else:
                p1 = 0
                p2 = 0
                spread = spread1
                bid_liquidity = calculate_liquidity(cex1_info['bids'][:p2+1])
                ask_liquidity = calculate_liquidity(cex2_info['asks'][:p1+1])

            res = {
                "cex_bid": cex1,
                "cex_ask": cex2,
                "bid_price": cex1_info['bids'][0][0],
                "bid_price_2": cex1_info['bids'][p2][0],
                "ask_price": cex2_info['asks'][0][0],
                "ask_price_2": cex2_info['asks'][p1][0],
                "spread": str(spread1),
                "spread_2": str(spread),
                "bid_liquidity": bid_liquidity,
                "ask_liquidity": ask_liquidity
            }
            return res
            # return (cex1, cex2, cex1_info['bids'][0][0], cex2_info['asks'][0][0], str(spread1), cex1_info['bids'][0][1], cex2_info['asks'][0][1])
        try:
            spread2 = (bids_cex2[0] - asks_cex1[0]) / asks_cex1[0]
        except:
            return None 
        if spread2 >= self.spread_limit:
            if False and spread2 >= 0.15:
                p1, p2, spread, liquidity = find_optimal_spread(cex1_info['asks'], cex2_info['bids'])
                
                bid_liquidity = calculate_liquidity(cex2_info['bids'][:p2+1])
                ask_liquidity = calculate_liquidity(cex1_info['asks'][:p1+1])

                if min(bid_liquidity, ask_liquidity) < self.liquidity_limit:
                    logging.debug(f"{symbol} {cex2}->{cex1} was reject because liquidity is too low")
                    return None
            else:
                p1 = 0
                p2 = 0
                spread = spread2
                bid_liquidity = calculate_liquidity(cex2_info['bids'][:p2+1])
                ask_liquidity = calculate_liquidity(cex1_info['asks'][:p1+1])

            res = {
                "cex_bid": cex2,
                "cex_ask": cex1,
                "bid_price": cex2_info['bids'][0][0],
                "bid_price_2": cex2_info['bids'][p2][0],
                "ask_price": cex1_info['asks'][0][0],
                "ask_price_2": cex1_info['asks'][p1][0],
                "spread": str(spread2),
                "spread_2": str(spread),
                "bid_liquidity": bid_liquidity,
                "ask_liquidity": ask_liquidity
            }
            return res 
            # return (cex2, cex1, cex2_info['bids'][0][0], cex1_info['asks'][0][0], str(spread2), cex2_info['bids'][0][1], cex1_info['asks'][0][1])
        
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
        self.last_buffer_update = None 

        while True:
            logging.debug(f"Iteration #{i} has started")
            self.update_symbols()
            self.update_chains()
            self.update_buffer()


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
            

            t_s = time.time()
            self.scan()
            t_e = time.time()

            logging.debug(f"Iteration #{i} has ended. It took {t_e - t_s} seconds")

            time.sleep(config.refresh_rate)
            i += 1

    def update_buffer(self):
        """
        Function clears buffer with spreads with particular interval
        """
        if not self.last_buffer_update or time.time() - self.last_buffer_update > self.buffer_update_interval:
            self.spreads_buffer.clear()
            
            self.last_buffer_update = time.time()

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


    def filter_spreads(self, spreads:list):
        """
        Function filters spreads by addtional conditions and add some extra info
        :param spreads: list of spreads
        :returns: list of filtered spreads
        """
        result = []
        for spread in spreads:
            if (spread['symbols'], spread['cex_ask'], spread['cex_bid']) in self.spreads_buffer:
                continue 

            res = []

            cex_ask = spread['cex_ask']
            cex_bid = spread['cex_bid']
            symbol = spread['symbols']
            token = symbol.split("/")[0]

            chains1 = self.markets[cex_ask].chains.get(token, {})
            chains2 = self.markets[cex_bid].chains.get(token, {})
            
            if not chains1 or not chains2:
                logging.debug(f"{symbol}{cex_ask}->{cex_bid} was reject because i couldn't get chain info")
                continue

            intersection = find_dicts_intersection(chains1, chains2)

            if len(intersection) == 0:
                logging.debug(f"{symbol}{cex_ask}->{cex_bid} was reject because i there is no same chains between these 2 cexes for this symbol")
                continue
            
            for chain in intersection:
                if not bool(chains1[chain]['withdraw']) or not bool(chains2[chain]['deposit']):
                    continue

                res.append(chain)
            
            if not res:
                logging.debug(f"{symbol}{cex_ask}->{cex_bid} was reject because there is withdraw or deposit are permitted on one of these 2 cexes for this symbol")
                continue

            
            min_fee = min([float(chains1[chain]['withdrawFee']) for chain in res])

            if min_fee == float('inf'):
                min_fee = min([float(chains2[chain]['withdrawFee']) for chain in res])



            spread['withdraw_fee'] = min_fee
            # spread['trading_fee'] = self.markets[cex_ask].TRADING_FEE + self.markets[cex_bid].TRADING_FEE
            spread['ask_trade_fee'] = self.markets[cex_ask].TRADING_FEE
            spread['bid_trade_fee'] = self.markets[cex_bid].TRADING_FEE
            spread['chains'] = res 

            result.append(spread)
        return result

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
        filtered_spreads = self.filter_spreads(spreads)

        logging.debug(f"Spreads have been found. Found {len(spreads)} spreads")


        for spread in filtered_spreads:
            self.spreads_buffer.add(
                (spread['symbols'], spread['cex_ask'], spread['cex_bid'])
            )

        for opportunity in filtered_spreads:
            for observer in self.observers:
                observer.opportunity(**opportunity) 

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
                    
                    scan = self._find_spread_by_two_cex(symbol, cex1, cex1_info, cex2, cex2_info)

                    if scan:
                        scan['symbols'] = symbol
                        # spreads.append(tuple(
                        #     list(scan) + [symbol]
                        # ))
                        spreads.append(scan)

                    cex_pairs.add((cex1, cex2))

        return spreads
    
    
