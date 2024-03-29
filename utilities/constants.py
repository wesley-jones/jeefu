# Constants used across packages
import datetime

BUY = 'Buy'
SELL = 'Sell'
HOLD = 'Hold'
ACTION = 'Action'

DATE = 'Date'
RECOMMENDATION = 'Recommendation'
CASH_BALANCE = 'Cash Balance'
BTC_BALANCE = 'BTC Balance'
PREVIOUS_TRANSACTION_CLOSE_PRICE = 'Previous Transaction Close Price'
CONSECUTIVE_DAYS_HOLDING_CASH = 'Consecutive Days Holding Cash'
CONSECUTIVE_DAYS_HOLDING_BTC = 'Consecutive Days Holding BTC'
LIST_CONSECUTIVE_DAYS_HOLDING_CASH = 'List of Consecutive Days Holding Cash'
LIST_CONSECUTIVE_DAYS_HOLDING_BTC = 'List of Consecutive Days Holding BTC'
LIST_RETURNS_PER_BUY = 'Returns per Buy'
LIST_RETURNS_PER_SELL = 'Returns per Sell'

CLOSE_PRICE = 'Close'
OPEN_PRICE = 'Open'
HIGH_PRICE = 'High'
LOW_PRICE = 'Low'

HISTORICAL_START_DATE = datetime.datetime(2014, 9, 17).date()
HISTORICAL_STARTING_CASH_BALANCE = 457.3340148925781 # Equals one Bitcoin on 9/17/2014

QUERY_ORDER_DATE_DESCENDING = '-' + DATE
QUERY_ORDER_DATE_ASCENDING = DATE
