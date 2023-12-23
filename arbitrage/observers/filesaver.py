from arbitrage.observers.observer import Observer
import json 


DEPTH_PATH = "depth.json"
OPPORTUNITIES_PATH = "opportunities.txt"

class FileSaver(Observer):
    def __init__(self) -> None:
        super().__init__()

    def save_depth(self, depth):
        """
        Saves state of orderbooks
        """
        with open(DEPTH_PATH, 'w') as file:
            json.dump(depth, file)

    def opportunity(self, profit, volume, buyprice, kask, sellprice, kbid, perc, weighted_buyprice, weighted_sellprice):    
        with open(OPPORTUNITIES_PATH, 'w') as file:
            file.write("profit: %f USD with volume: %f BTC - buy from %s sell to %s ~%.2f%%" % (profit, volume, kask, kbid, perc), file)
            file.write("\n")

    
    

