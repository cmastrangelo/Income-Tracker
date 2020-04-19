import json
import datetime
from iexfinance.stocks import get_historical_data, Stock
from decimal import Decimal
from keys import iexkey


class Trading_Tracker:
    def __init__(self):
        self.orders = self.load_orders()

    def convert_to_datetime(self, date):
        return datetime.datetime.strptime(date, '%Y-%m-%d')

    def get_iex_price(self, date, symbol):
        start = date
        end = date
        response = get_historical_data(symbol, start, end, token=iexkey.iexkey)
        if response == {}:
            return response
        for r in response:
            return response[r]

    def load_orders(self):
        with open('data/trades.json', 'r') as f:
            return json.loads(f.read())

    def get_actual_dividend(self, from_date, end=None):
        unique_stocks = self.get_all_unique_stocks(from_date, end)
        dividend_data = {}
        for symbol in unique_stocks:
            stock_dividend_data = Stock(symbol, token=iexkey.iexkey).get_dividends(range='1y')
            dividend_data[symbol] = stock_dividend_data
        total_dividend_payout = Decimal('0')
        for symbol in unique_stocks:
            for dividend_pay_data in dividend_data[symbol]:
                payday_date = self.convert_to_datetime(dividend_pay_data['exDate'])
                stocks, cash_used_after_date = self.prepare_stocks_and_cash_for_date(payday_date)
                if symbol in stocks and dividend_pay_data['amount'] != '':
                    print(symbol, dividend_pay_data)
                    print(round(Decimal(str(stocks[symbol])) * Decimal(dividend_pay_data['amount']), 2))
                    total_dividend_payout += round(Decimal(str(stocks[symbol])) * Decimal(dividend_pay_data['amount']), 2)
        print(total_dividend_payout)
        return total_dividend_payout

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

    def get_account_value_at(self, from_date):
        print(from_date)
        stocks, cash_used_after_date = self.prepare_stocks_and_cash_for_date(from_date)
        print(stocks)

        starting_business_day = from_date
        starting_value_on_date = Decimal('0')
        for stock in stocks:
            price = self.get_iex_price(starting_business_day, stock)
            while price == {}:
                starting_business_day -= datetime.timedelta(days=1)
                price = self.get_iex_price(starting_business_day, stock)
            equity = Decimal(str(price['close'])) * Decimal(str(stocks[stock]))
            starting_value_on_date += equity
        return starting_value_on_date, cash_used_after_date

    def get_profit_from(self, from_date, end=None):
        value_on_date, cash_used_after_date = self.get_account_value_at(from_date)
        print(value_on_date, cash_used_after_date)
        total_cash_invested = value_on_date + cash_used_after_date
        print('Total started with:', total_cash_invested)
        if end is None:
            value_on_date, cash_used_after_date = self.get_account_value_at(datetime.datetime.now())
        else:
            print('this thingy')
            value_on_date, cash_used_after_date = self.get_account_value_at(end)
        print(value_on_date, cash_used_after_date)
        print('Profit in this timeframe:', value_on_date - total_cash_invested)
        return value_on_date - total_cash_invested

    def get_full_return(self, from_date, end=None):
        total_profit = self.get_profit_from(from_date, end)
        total_dividend = self.get_actual_dividend(from_date, end=None)
        print('Total from price fluctuations', total_profit)
        print('Total from dividends', total_dividend)
        print('Total profit', total_profit + total_dividend)

    def prepare_stocks_and_cash_for_date(self, from_date):
        stocks = {}
        cash_used_after_date = Decimal('0')
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
                for order in self.orders[date]:
                    cash_used_after_date += Decimal(str(order['shares'])) * Decimal(str(order['price']))
        return stocks, cash_used_after_date


if __name__ == '__main__':
    tt = Trading_Tracker()
    #two_weeks_ago = datetime.datetime.now() - datetime.timedelta(days=14)
    #tt.get_profit_from(datetime.datetime(2019, 9, 17), end=datetime.datetime(2020, 2, 25))
    #tt.get_monthly_dividend()
    tt.get_full_return(datetime.datetime(2019, 9, 17))
