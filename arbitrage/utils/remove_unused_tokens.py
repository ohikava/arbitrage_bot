def check_symbol_at_least_on_two_exc(symbol:str, exchanges: list):
    """
    Check if the symbol is available on at least 2 exchanges
    """
    count = 0
    for exchange in exchanges:
        if symbol in exchange:
            count += 1
            
    return count >= 2

if __name__ == "__main__":

    exchanges = ['bybit', 'bitget', 'mexc', 'bingx']

    exchanges_tokens = []

    for exchange in exchanges:
        with open(f'/home/ivannewest/projects/arbitrage/symbols/{exchange}.txt') as file:
            data = file.readlines()
        data = [i.strip() for i in data]
        exchanges_tokens.append(data)

    
    with open('/home/ivannewest/projects/arbitrage/symbols/all.txt') as file:
        data = file.readlines()

    data = [i.strip() for i in data]

    new_data = []
    i = 0
    for token in data:
        if not check_symbol_at_least_on_two_exc(token, exchanges_tokens):
            print(token)
            i += 1
            continue 
        new_data.append(token)
    print(f"Total: {i} symbols were removed")


    with open('/home/ivannewest/projects/arbitrage/symbols/all.txt', "w") as file:
        for token in new_data:
            file.write(f"{token}\n")

    