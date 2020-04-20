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


def update_all_snapshots_required():
    pass


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
    run_menu()
