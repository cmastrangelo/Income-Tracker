import json
import datetime
from iexfinance.stocks import get_historical_data, Stock
from decimal import Decimal
from keys import iexkey
from tabulate import tabulate
from colorama import init
from termcolor import colored


class Trading_Tracker:
    def __init__(self, trades_location='Trading/data/'):
        self.trades_location = trades_location
        self.orders = self.load_orders()

    def calculate_total_profit_dividend_each_symbol(self, total_profit_each_symbol, total_dividend_each_symbol):
        total_profit_dividend_each_symbol = {}
        for symbol in total_profit_each_symbol:
            total_profit_dividend_each_symbol[symbol] = total_profit_each_symbol[symbol]
            if symbol in total_dividend_each_symbol:
                total_profit_dividend_each_symbol[symbol] += total_dividend_each_symbol[symbol]
        return total_profit_dividend_each_symbol

    def calculate_profit_overall(self, total_profit_dividend_each_symbol):
        total_overall = Decimal('0')
        for symbol in total_profit_dividend_each_symbol:
            total_overall += total_profit_dividend_each_symbol[symbol]
        return total_overall

    def convert_to_datetime(self, date):
        return datetime.datetime.strptime(date, '%Y-%m-%d')

    def display_full_return_table(
            self,
            total_profit_each_symbol,
            total_dividend_each_symbol,
            total_profit_dividend_each_symbol,
            total_profit_overall
    ):
        table = [['Symbol', 'Trading Profit', 'Dividend Profit', 'Total']]
        for symbol in total_profit_each_symbol:
            table.append([
                symbol,
                colored(total_profit_each_symbol[symbol], 'green' if total_profit_each_symbol[symbol] >= 0 else 'red'),
                '' if symbol not in total_dividend_each_symbol else colored(total_dividend_each_symbol[symbol], 'green' if total_dividend_each_symbol[symbol] >= 0 else 'red'),
                colored(total_profit_dividend_each_symbol[symbol], 'green' if total_profit_dividend_each_symbol[symbol] >= 0 else 'red')
            ])
        total_trading_overall = Decimal('0')
        total_dividend_overall = Decimal('0')
        for symbol in total_profit_each_symbol:
            total_trading_overall += total_profit_each_symbol[symbol]
            if symbol in total_dividend_each_symbol:
                total_dividend_overall += total_dividend_each_symbol[symbol]
        table.append([
            'Total',
            colored(total_trading_overall, 'green' if total_trading_overall >= 0 else 'red'),
            colored(total_dividend_overall, 'green' if total_dividend_overall >= 0 else 'red'),
            colored(total_profit_overall, 'green' if total_profit_overall >= 0 else 'red')
        ])
        print(tabulate(table, headers="firstrow", tablefmt="github"))

    def get_iex_price(self, date, symbol):
        start = date
        end = date
        response = get_historical_data(symbol, start, end, token=iexkey.iexkey)
        if response == {}:
            return response
        for r in response:
            return response[r]

    def load_orders(self):
        with open(self.trades_location + 'trades.json', 'r') as f:
            return json.loads(f.read())

    def get_actual_dividend(self, from_date, end=None):
        unique_stocks = self.get_all_unique_stocks(from_date, end)
        dividend_data_each_symbol = {}
        for symbol in unique_stocks:
            stock_dividend_data = Stock(symbol, token=iexkey.iexkey).get_dividends(range='1y')
            dividend_data_each_symbol[symbol] = stock_dividend_data
        total_dividend_payout_each_symbol = {}
        for symbol in unique_stocks:
            for dividend_pay_data in dividend_data_each_symbol[symbol]:
                payday_date = self.convert_to_datetime(dividend_pay_data['exDate'])
                stocks, cash_used_after_date = self.prepare_stocks_and_cash_for_date(payday_date)
                if symbol in stocks and dividend_pay_data['amount'] != '':
                    if symbol not in total_dividend_payout_each_symbol:
                        total_dividend_payout_each_symbol[symbol] = round(Decimal(str(stocks[symbol])) * Decimal(dividend_pay_data['amount']), 2)
                    else:
                        total_dividend_payout_each_symbol[symbol] += round(Decimal(str(stocks[symbol])) * Decimal(dividend_pay_data['amount']), 2)
        return total_dividend_payout_each_symbol

    def get_all_unique_stocks(self, from_date, end=None):
        stocks, cash_used_after_date = self.prepare_stocks_and_cash_for_date(from_date)
        unique_stocks = []
        for stock in stocks:
            unique_stocks.append(stock)
        for date in self.orders:
            if self.convert_to_datetime(date) >= from_date:
                if (end is not None and self.convert_to_datetime(date) <= end) or end is None:
                    for trade in self.orders[date]:
                        if trade['symbol'] not in unique_stocks:
                            unique_stocks.append(trade['symbol'])
        return unique_stocks

    def get_monthly_dividend(self):
        stocks, cash_used_after_date = self.prepare_stocks_and_cash_for_date(datetime.datetime.now())
        print(stocks)
        total_monthly_dividend = Decimal('0')
        for stock in stocks:
            print(stock)
            dividend_data = Stock(stock, token=iexkey.iexkey).get_dividends(range='1y')
            print(dividend_data)
            if dividend_data != []:
                if dividend_data[0]['frequency'] == 'quarterly':
                    quarterly_payment = Decimal(str(dividend_data[0]['amount'])) * Decimal(str(stocks[stock]))
                    print('qp:', quarterly_payment)
                    total_monthly_dividend += quarterly_payment / Decimal('3')
                else:
                    print('wtf is this shit?')
                    print(dividend_data['frequency'])
        print(total_monthly_dividend)

    def get_account_value_at(self, from_date, end = None):
        stocks, cash_used_after_date_each_symbol = self.prepare_stocks_and_cash_for_date(from_date, end)

        starting_business_day = from_date
        starting_value_on_date_each_symbol = {}
        for symbol in stocks:
            if symbol not in starting_value_on_date_each_symbol:
                starting_value_on_date_each_symbol[symbol] = Decimal('0')
            price = self.get_iex_price(starting_business_day, symbol)
            while price == {}:
                starting_business_day -= datetime.timedelta(days=1)
                price = self.get_iex_price(starting_business_day, symbol)
            equity = Decimal(str(price['close'])) * Decimal(str(stocks[symbol]))
            starting_value_on_date_each_symbol[symbol] += equity
        return starting_value_on_date_each_symbol, cash_used_after_date_each_symbol

    def get_profit_from(self, from_date, end=None):
        value_on_date_each_symbol, cash_used_after_date_each_symbol = self.get_account_value_at(from_date, end)
        total_cash_invested_each_symbol = {}
        for symbol in value_on_date_each_symbol:
            total_cash_invested_each_symbol[symbol] = value_on_date_each_symbol[symbol]
        for symbol in cash_used_after_date_each_symbol:
            if symbol in total_cash_invested_each_symbol:
                total_cash_invested_each_symbol[symbol] += cash_used_after_date_each_symbol[symbol]
            else:
                total_cash_invested_each_symbol[symbol] = cash_used_after_date_each_symbol[symbol]
        if end is None:
            value_on_date_each_symbol, cash_used_after_date_each_symbol = self.get_account_value_at(datetime.datetime.now(), end)
        else:
            value_on_date_each_symbol, cash_used_after_date_each_symbol = self.get_account_value_at(end, end)
        final_profit_for_each_symbol = {}
        for symbol in value_on_date_each_symbol:
            final_profit_for_each_symbol[symbol] = value_on_date_each_symbol[symbol] - total_cash_invested_each_symbol[symbol]
        return final_profit_for_each_symbol

    def get_full_return(self, from_date, end=None):
        print('Downloading prices...')
        total_profit_each_symbol = self.get_profit_from(from_date, end)
        print('Downloading dividends data...')
        total_dividend_each_symbol = self.get_actual_dividend(from_date, end=None)
        total_profit_dividend_each_symbol = self.calculate_total_profit_dividend_each_symbol(
            total_profit_each_symbol,
            total_dividend_each_symbol
        )
        total_profit_overall = self.calculate_profit_overall(total_profit_dividend_each_symbol)
        self.display_full_return_table(total_profit_each_symbol, total_dividend_each_symbol, total_profit_dividend_each_symbol, total_profit_overall)

    def prepare_stocks_and_cash_for_date(self, from_date, end=None):
        stocks = {}
        cash_used_after_date_each_symbol = {}
        for date in self.orders:
            if self.convert_to_datetime(date) < from_date:
                for order in self.orders[date]:
                    if order['type'] == "buy":
                        if order['symbol'] in stocks:
                            stocks[order['symbol']] += order['shares']
                        else:
                            stocks[order['symbol']] = order['shares']
                    if order['type'] == "sell":
                        # Probably will need to adjust cash_used_after_date once we have sell orders
                        stocks[order['symbol']] -= order['shares']
            if self.convert_to_datetime(date) >= from_date:
                if end is not None and self.convert_to_datetime(date) >= end:
                    break
                for order in self.orders[date]:
                    if order['symbol'] not in cash_used_after_date_each_symbol:
                        cash_used_after_date_each_symbol[order['symbol']] = Decimal('0')
                    cash_used_after_date_each_symbol[order['symbol']] += Decimal(str(order['shares'])) * Decimal(str(order['price']))
        return stocks, cash_used_after_date_each_symbol


if __name__ == '__main__':
    init()  # Initializes the colorama for colored text
    tt = Trading_Tracker(trades_location='data/')
    #two_weeks_ago = datetime.datetime.now() - datetime.timedelta(days=14)
    #tt.get_profit_from(datetime.datetime(2019, 9, 17), end=datetime.datetime(2020, 2, 25))
    #tt.get_monthly_dividend()
    tt.get_full_return(datetime.datetime(2019, 9, 17))
