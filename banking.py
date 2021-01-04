# Write your code here
import random
import sqlite3
import os


class Bank:
    def __init__(self):
        db = 'card.s3db'
        db_is_new = not os.path.exists(db)
        self.conn = sqlite3.connect(db)
        self.cursor = self.conn.cursor()
        if db_is_new:
            self.cursor.execute("""
            create table card(
            id integer,
            number text,
            pin text,
            balance integer default 0);""")
            self.conn.commit()
        self.id = 0
        self.menu()

    @property
    def accounts(self):
        self.cursor.execute('select number from card')
        return self.cursor.fetchall()

    @property
    def main_operation(self):
        return self._main_operation

    @main_operation.setter
    def main_operation(self, op):
        self._main_operation = op
        if op == '1':
            self.create_account()
        elif op == '2':
            self.login()
        elif op == '0':
            self.goodbye()
        else:
            self.warning()
            self.menu()

    def create_account(self):
        number = f'{400000}{random.randint(0, 1e9):09d}'
        number += self.checksum(number)
        pin = f'{random.randint(0, 1e4):04d}'
        if number not in self.accounts:
            self.id += 1
            self.cursor.execute(f'insert into card (id, number, pin) values ({self.id}, {number}, {pin})')
            self.conn.commit()
            print(self.get_balance(number))
        else:
            self.create_account()
        print(f'''Your card has been created
Your card number:
{number}
Your card PIN:
{pin}
''')
        self.menu()

    def login(self):
        self.login_interface()

    def login_interface(self):
        while True:
            number = input('Enter you card number:\n')
            if not number:
                print('Card number cannot be empty!')
            else:
                break
        while True:
            pin = input('Enter your PIN:\n')
            if not pin:
                print('PIN cannot be empty!')
            else:
                break
        self.cursor.execute(f'select number, pin from card where number = {number} and pin = {pin};')
        result_of_query = self.cursor.fetchone()
        print(result_of_query)
        if not result_of_query:
            print('Wrong card number or PIN!')
            self.menu()
        else:
            print('You have successfully logged in!\n')
            self.account_menu(number)

    def account_menu(self, number):
        operation = input("""1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit
""")
        if operation == '1':
            balance = self.get_balance(number)
            print(f"Balance: {balance}")
            self.account_menu(number)
        elif operation == '2':
            self.add_income(number)
        elif operation == '3':
            self.do_transfer(number)
        elif operation == '4':
            self.close_account(number)
        elif operation == '5':
            print('You have successfully logged out!')
            self.menu()
        elif operation == '0':
            self.goodbye()
        else:
            self.warning()
            self.account_menu(number)

    def menu(self, op=None):
        if not op:
            op = input('''1. Create an account
2. Log into account
0. Exit
''')
        self.main_operation = op

    @staticmethod
    def warning():
        print('Invalid input!')

    @staticmethod
    def goodbye():
        print('Bye!')

    @staticmethod
    def checksum(number_string):
        total = 0
        for n, d in enumerate(number_string):
            d = int(d)
            d = d * 2 if n % 2 == 0 else d
            d = d - 9 if d > 9 else d
            total += d
        remainder = total % 10
        return str(10 - remainder if remainder != 0 else 0)

    def validator(self, number):
        checksum = self.checksum(number[:-1])
        if checksum == number[-1]:
            return True
        else:
            return False

    def add_income(self, number):
        while True:
            income = input('Enter income:\n')
            try:
                income = int(income)
            except ValueError:
                print('Invalid input, try again!\n')
                continue
            else:
                balance = self.get_balance(number)
                balance += income
                self.cursor.execute(f'''update card
                                       set balance = {balance}
                                       where number = {number}''')
                self.conn.commit()
                print(self.get_balance(number))
                print('Income was added')
                self.account_menu(number)
                break

    def get_balance(self, number):
        self.cursor.execute(f'select balance from card where number = {number}')
        balance = self.cursor.fetchone()[0]
        return balance

    def do_transfer(self, number):
        balance = self.get_balance(number)
        while True:
            dest_account = input('Transfer\nEnter card number:\n')
            if dest_account == number:
                print("You can't transfer money to the same account!")
                self.account_menu()
            else:
                self.cursor.execute(f'select number from card where number = {dest_account}')
                if not self.validator(dest_account):
                    print("Probably you made a mistake in the card number. Please try again!")
                    self.account_menu(number)
                elif not self.cursor.fetchone():
                    print("Such a card does not exist.")
                    self.account_menu(number)
                else:
                    while True:
                        transfer_amount = input('Enter how much money do you want to transfer:\n')
                        try:
                            transfer_amount = int(transfer_amount)
                        except ValueError:
                            print('Invalid input, try again!')
                            continue
                        else:
                            if transfer_amount > balance:
                                print('Not enough money!')
                                self.account_menu(number)
                            else:
                                self.cursor.execute(f'''
                                update card set balance = balance - {transfer_amount} where number = {number};
                                ''')
                                self.cursor.execute(f'''
                                update card set balance = balance + {transfer_amount} where number = {dest_account};
                                ''')
                                self.conn.commit()
                                print('Success!')
                                self.account_menu(number)
                        break
            break

    def close_account(self, number):
        self.cursor.execute(f'''
        delete from card where number = {number}''')
        self.conn.commit()
        self.menu()


if __name__ == '__main__':
    bank = Bank()
