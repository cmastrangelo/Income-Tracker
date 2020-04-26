import json
from helper import convert_to_datetime
from Trading.Trading_Tracker import Trading_Tracker
import datetime


def get_latest_income():
    with open('Job/income.json', 'r') as f:
        data = json.loads(f.read())
    latest_date = ''
    for date in data:
        if latest_date == '':
            latest_date = date
        else:
            if convert_to_datetime(date) > convert_to_datetime(latest_date):
                latest_date = date
    print('This shit right here won my brother:', latest_date, data[latest_date])
    return latest_date, data[latest_date]


def get_income_data():
    with open('data/job/income.json', 'r') as f:
        return json.loads(f.read())


def get_snapshots_data():
    with open('data/snapshots/snapshots.json', 'r') as f:
        return json.loads(f.read())


def save_snapshots_data(snapshot_data):
    with open('data/snapshots/snapshots.json', 'w') as f:
        json.dump(f, snapshot_data)


def update_all_snapshots_required():
    income_data = get_income_data()
    snapshot_data = get_snapshots_data()
    tt = Trading_Tracker()
    previous_payday = 0
    for income_date in income_data:
        if income_date not in snapshot_data:
            print('Adding', income_date)
            if previous_payday == 0:
                trading_profit = 0
            else:
                trading_profit = tt.calculate_total_profit_all_symbols(
                    tt.get_profit_from(
                        convert_to_datetime(previous_payday),
                        convert_to_datetime(income_date)
                    )
                )
            snapshot_data[income_date] = {'income': income_data[income_date], 'trading': trading_profit}
        previous_payday = income_date
    save_snapshots_data(snapshot_data)


def snapshot_stats():
    snapshots_data = get_snapshots_data()
    yearly_data = {}




def run_menu():
    tt = Trading_Tracker()
    while True:
        print('1 - Update all income keys without a snapshot pair.')
        print('2 - Get full report of trading and dividends profit')
        i = input()
        if i == '1':
            update_all_snapshots_required()
        if i == '2':
            tt.get_full_return(datetime.datetime(2019, 9, 17))


if __name__ == "__main__":
    # Getting full income for payperiod
    #latest_income_date, income_amount = get_latest_income()
    #run_menu()
    update_all_snapshots_required()
