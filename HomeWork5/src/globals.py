import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = 'database.db'
USERS_TN = 'users'
BANKS_TN = 'banks'
ACCOUNTS_TN = 'accounts'
TRANSACTIONS_TN = 'transactions'

API_URL_CURRENCIES = 'https://api.freecurrencyapi.com/v1/latest'
API_KEY_CURRENCIES = os.getenv('API_KEY_CURRENCIES')

AVAILABLE_DISCOUNTS = [25, 30, 50]

VALID_TYPES = ['credit', 'debit']
VALID_STATUSES = ['gold', 'silver', 'platinum']
