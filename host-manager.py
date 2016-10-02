#!/bin/python3

import sqlite3

db = sqlite3.connect('data/customer.db')
cursor = db.cursor()

cursor.execute(
    '''
    CREATE TABLE customers(id INTEGER PRIMARY KEY, fullname TEXT, agency TEXT, nights INTEGER)
    '''
    )

db.commit()

new_customer = {'fullname':'Alessia', 'nights': 3}

cursor.execute(
    '''
    INSERT INTO customers(fullname, nights)
    VALUES(:fullname, :nights)
    ''',
    new_customer)

db.commit()

cursor.execute('''SELECT fullname, agency, nights FROM customers''')
all_customers = cursor.fetchall()

for customer in all_customers:
    print(customer)
                           
