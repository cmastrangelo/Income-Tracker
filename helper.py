import datetime


def convert_to_datetime(date):
    return datetime.datetime.strptime(date, '%m-%d-%Y')