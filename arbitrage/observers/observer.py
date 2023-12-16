import abc


class Observer(object, metaclass=abc.ABCMeta):
    def start_search(self, depths):
        pass

    def end_search(self):
        pass

    @abc.abstractmethod
    def opportunity(
        self,
        profit,
        volume,
        buyprice,
        kask,
        sellprice,
        kbid,
        perc,
        weighted_buyprice,
        weighted_sellprice,
    ):
        pass
