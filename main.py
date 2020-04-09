import json
from helper import convert_to_datetime
from Trading.Trading_Tracker import Trading_Tracker


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


if __name__ == "__main__":
    # Getting full income for payperiod
    latest_income_date, income_amount = get_latest_income()
