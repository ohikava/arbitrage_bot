def find_dicts_intersection(dict1: dict, dict2: dict) -> dict:
    """
    Find intersection of dicts
    """
    return set(dict1.keys()) & set(dict2.keys())
    

def get_spread(a:tuple, b:tuple)->float:
    """
    Give two tuples (price, amount) return spread
    """
    return (float(b[0]) - float(a[0])) / float(a[0])

def calculate_liquidity(a: list)-> float:
    """
    Calculate accamulative liquidity of a list of tuples (price, amount)
    """
    return sum([float(i[1])*float(i[0]) for i in a])

def find_optimal_spread(a:list, b:list, spread_decrease_lim:float=0.3, spread_lim:float=0.03, liq_lim:float=100.0):
    """
    Searches for the best tradeoff between spread and liquidity
    :param a: list of tuples (price, amount) for the cex where we are buying
    :param b: list of tuples (price, amount) for the cex where we are selling
    :param spread_decrease_lim: how much spread can decrease(0.3 means 30%)
    :param spread_lim: the spread value that satisfies us and we don't look at decrease 
    :param liq_lim: the liquidity value that satisfies us and we stop looking for better trades
    :return: index of the best tradeoff, spread, liquidity
    """
    p1 = 0
    p2 = 0
    min_spread = get_spread(a[0], b[0]) 
    spread = min_spread

    min_liq = min(float(a[0][1])*float(a[0][0]), float(b[0][1])*float(b[0][0]))

    q = 1
    stop_p1 = False
    stop_p2 = False 
    while p1 < len(a)-1 or p2 < len(b)-1:
        if min_liq >= liq_lim:
            return p1, p2, min_spread, min_liq
        
        if stop_p1 and stop_p2:
            break

        if stop_p1:
            q = 0 
        
        if stop_p2:
            q = 1

        if q and p1 < len(a)-1:
            c = get_spread(a[p1+1], b[p2])
            if not (c < spread * (1-spread_decrease_lim)) or c >= spread_lim:
                p1 += 1
                q = 0
                min_spread = c 
                min_liq = min(calculate_liquidity(a[:p1+1]), calculate_liquidity(b[:p2+1]))
            else:
                stop_p1 = True 

            continue 
            


        if not q and p2 < len(b)-1:
            c = get_spread(a[p1], b[p2+1])
            if not (c < spread * (1-spread_decrease_lim)) or c >= spread_lim:
                p2 += 1
                q = 1
                min_spread = c 
                min_liq = min(calculate_liquidity(a[:p1+1]), calculate_liquidity(b[:p2+1]))

            else:
                stop_p2 = True
            continue 

    return p1, p2, min_spread, min_liq