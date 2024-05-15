from os import getenv
from dotenv import load_dotenv

load_dotenv()

ID_REGEX = r'[a-zA-Z]{1,3}-\d+'
SPECIAL_CHARACTERS_REGEX = r'[#%_?&]'
FULL_NAME_CLEAR_REGEX = r'[^a-zA-Z\s]'

DB_NAME = 'database.db'

USERS_TN = 'users'
BANKS_TN = 'banks'
ACCOUNTS_TN = 'accounts'

STATUS_CN = 'status'
TYPE_CN = 'type'
NUMBER_CN = 'number'

TRANSACTIONS_TN = 'transactions'

API_URL_CURRENCIES = 'https://api.freecurrencyapi.com/v1/latest'
API_KEY_CURRENCIES = getenv('API_KEY_CURRENCIES')

ALLOWED_ACCOUNT_LENGTH = 18
AVAILABLE_DISCOUNTS = [25, 30, 50]

VALID_ACCOUNT_NUMBER_START = 'ID--'
VALID_DATETIME_PATTERN = '%Y-%m-%d %H:%M:%S'

VALID_TYPES = ['credit', 'debit']
VALID_STATUSES = ['gold', 'silver', 'platinum']
