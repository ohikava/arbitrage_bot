import unittest 
from arbitrage.arbitrage_bot import ArbitrageBot
import json 

# python -m unittest test_module.py

class TestSpreadSearch(unittest.TestCase):
    def setUp(self):
        self.arbitrage_bot = ArbitrageBot()
        self.maxDiff = None

        with open("tests/fake_spreads.json") as file:
            self.fake_spreads = json.load(file)


    def test_spread_search(self):
        spreads = self.arbitrage_bot.find_spread(self.fake_spreads)

        spreads_true = [
            ("Bitget", "Bybit", "14", "13", str((14-13)/13), "20.0", "ETH/USDT"),
            ("MEXC", "BingX", "1", "0.6", str((1-0.6)/0.6), "5.0", "BTC/USDC"),
        ]

        self.assertCountEqual(spreads, spreads_true)
