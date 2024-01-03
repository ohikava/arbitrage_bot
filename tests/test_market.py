import unittest 
from arbitrage.cex.bitget import BitGet
from arbitrage.cex.bybit import ByBit

# python -m unittest test_module.py

class TestSpreadSearch(unittest.TestCase):
    def setUp(self):
        self.bybit = ByBit()
        self.biget = BitGet()


    def test_symbol_listed(self):
        symbol = "BTC/USDT"

        bybit = self.bybit.check_symbol_listed(symbol)
        bitget = self.biget.check_symbol_listed(symbol)

        self.assertEqual((bybit, bitget), (True, True))
        