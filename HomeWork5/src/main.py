from HomeWork5.src.db_tasks_sql import get_user_transactions
from db_tasks import get_users_full_names_with_debts, get_biggest_capital_bank, get_banks_with_oldest_client, \
    get_bank_with_most_unique_outbound_operations, delete_empty_users
from api import add_banks, add_accounts, add_users, update_user, update_account
from globals import USERS_TN, BANKS_TN, ACCOUNTS_TN, TRANSACTIONS_TN
from transactions import perform_transaction
from utils import generate_discounts, clear_table

if __name__ == '__main__':
    users = [
        {'full_name': 'Andrey Andreev', 'birth_day': '2000-08-04', 'accounts': 'ID--k4-bfe-12363-v,ID--m2-ef-74532-ls'},
        {'full_name': 'Danil Danilov', 'birth_day': '2001-01-15', 'accounts': 'ID--r3-dd-32224-ja,ID--p7-cd-98236-tf'}
    ]
    banks = [
        {'name': 'Privat'},
        {'name': 'Mono'}
    ]
    accounts = [
        {'user_id': 1, 'type': 'debit', 'number': 'ID--k4-bfe-12363-v', 'bank_id': 1, 'currency': 'USD',
         'amount': 7773, 'status': 'silver'},
        {'user_id': 2, 'type': 'credit', 'number': 'ID--r3-dd-32224-ja', 'bank_id': 2, 'currency': 'EUR',
         'amount': 5555, 'status': 'gold'},
        {'user_id': 2, 'type': 'debit', 'number': 'ID--p7-cd-98236-tf', 'bank_id': 2, 'currency': 'GBP',
         'amount': -9999, 'status': 'platinum'},
        {'user_id': 1, 'type': 'credit', 'number': 'ID--m2-ef-74532-ls', 'bank_id': 2, 'currency': 'USD',
         'amount': 12345, 'status': 'gold'},
    ]

    clear_table(USERS_TN)
    clear_table(BANKS_TN)
    clear_table(ACCOUNTS_TN)
    clear_table(TRANSACTIONS_TN)

    add_banks(banks)
    add_accounts(accounts)
    add_users(users)

    update_user({'name': 'Evgen'}, 1)

    update_account({'type': 'debit'}, 1)

    perform_transaction('ID--k4-bfe-12363-v', 'ID--r3-dd-32224-ja', 5000)

    perform_transaction('ID--r3-dd-32224-ja', 'ID--k4-bfe-12363-v', 5000)

    perform_transaction('ID--m2-ef-74532-ls', 'ID--k4-bfe-12363-v', 222)

    print(generate_discounts(2))
    print(get_users_full_names_with_debts())
    print(get_biggest_capital_bank())
    print(get_banks_with_oldest_client())
    print(get_bank_with_most_unique_outbound_operations())
    print(get_user_transactions(1, 30))
    delete_empty_users()
