import json

def load_mining_data():
    with open("data.json") as f:
        return json.loads(f.read())


if __name__ == "__main__":
    # Function to calculate cost/day
    # E(kWh/day) = P(W) * t(h/day) / 1000 (W/kW)
    # Cost($/day) = E(kWh/day) * cost(cent/kWh) / 100(cent/$)
    mining_data = load_mining_data()
    watt_usage = mining_data['watt_usage']
    cents_per_kWh = 5.6
    E = watt_usage * 24 / 1000
    cost_per_day = E * cents_per_kWh / 100
    cost_per_week = cost_per_day * 7
    cost_per_month = round(cost_per_day * 30, 2)
    print(cost_per_day)
    print(cost_per_week)
    print(cost_per_month, 2)

    ethereum_per_month = mining_data['ethereum_per_month']
    monero_per_month = mining_data['monero_per_month']

    # @ Ethereum 141.86
    # @ Monero 51.02
    print('At Ethereum 141.86 and Monero 51.02')
    profit = (ethereum_per_month * 141.86) + (monero_per_month * 51.02) - cost_per_month
    print(profit)

    # @ Ethereum 200
    # @ Monero 60
    print('At Ethereum 200 and Monero 60')
    profit = (ethereum_per_month * 200) + (monero_per_month * 60) - cost_per_month
    print(profit)

    # @ Ethereum 300
    # @ Monero 70
    print('At Ethereum 300 and Monero 70')
    profit = (ethereum_per_month * 300) + (monero_per_month * 70) - cost_per_month
    print(profit)

    # @ Ethereum 700
    # @ Monero 100
    print('At Ethereum 700 and Monero 100')
    profit = (ethereum_per_month * 700) + (monero_per_month * 100) - cost_per_month
    print(profit)

    # @ Ethereum 1000
    # @ Monero 140
    print('At Ethereum 1000 and Monero 140')
    profit = (ethereum_per_month * 1000) + (monero_per_month * 140) - cost_per_month
    print(profit)

    # @ Ethereum 1400
    # @ Monero 200
    print('At Ethereum 1400 and Monero 200')
    profit = (ethereum_per_month * 1400) + (monero_per_month * 200) - cost_per_month
    print(profit)