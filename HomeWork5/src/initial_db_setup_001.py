import argparse as argp
import sqlite3
from globals import DB_NAME, BANKS_TN, TRANSACTIONS_TN, USERS_TN, ACCOUNTS_TN


parser = argp.ArgumentParser()
parser.add_argument('--unique', action='store_true',
                    help=f'Uniqueness for fields {USERS_TN}.name and {USERS_TN}.surname')
args = parser.parse_args()
unique_constraint = 'UNIQUE' if args.unique else ''
connection = sqlite3.connect(DB_NAME)
cursor = connection.cursor()

cursor.execute(f'''CREATE TABLE IF NOT EXISTS {BANKS_TN} (
                        id INTEGER PRIMARY KEY,
                        name VARCHAR(255) UNIQUE NOT NULL
                    )''')

cursor.execute(f'''CREATE TABLE IF NOT EXISTS {TRANSACTIONS_TN} (
                        id INTEGER PRIMARY KEY,
                        bank_sender_name VARCHAR(255) NOT NULL,
                        bank_receiver_name VARCHAR(255) NOT NULL,
                        account_sender_id INTEGER NOT NULL,
                        account_receiver_id INTEGER NOT NULL,
                        sent_currency VARCHAR(50) NOT NULL,
                        sent_amount DECIMAL(10, 2) NOT NULL,
                        datetime DATETIME,
                        FOREIGN KEY (account_sender_id) REFERENCES accounts(id),
                        FOREIGN KEY (account_receiver_id) REFERENCES accounts(id)
                    )''')

cursor.execute(f'''CREATE TABLE IF NOT EXISTS {USERS_TN} (
                        id INTEGER PRIMARY KEY,
                        name VARCHAR(100) NOT NULL {unique_constraint},
                        surname VARCHAR(100) NOT NULL {unique_constraint},
                        birth_day DATE,
                        accounts TEXT NOT NULL
                    )''')

cursor.execute(f'''CREATE TABLE IF NOT EXISTS {ACCOUNTS_TN} (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        type VARCHAR(20) NOT NULL,
                        number VARCHAR(50) UNIQUE NOT NULL,
                        bank_id INTEGER NOT NULL,
                        currency VARCHAR(10) NOT NULL,
                        amount DECIMAL(10, 2) NOT NULL,
                        status VARCHAR(20),
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        FOREIGN KEY (bank_id) REFERENCES banks(id)
                    )''')

connection.commit()
connection.close()
