#!/bin/python3

import os
import sqlite3
import tkinter
import datetime

from tkinter.ttk import *
from collections import OrderedDict as odict

from pages_container import *
from insert_page import *
from customers_view import *
from home_page import *

if __name__ == "__main__":

    db = sqlite3.connect('data/db/customer.db')
    cursor = db.cursor()
    
    cursor.execute(
        '''
        SELECT * FROM sqlite_master WHERE name ='Customers' and type='table'
        '''
    )
    if not cursor.fetchone():
        cursor.execute(
            '''
            CREATE TABLE Customers(id INTEGER PRIMARY KEY, fullname TEXT, phone TEXT, building TEXT, room TEXT, 
            arrival DATE, departure DATE, nights INTEGER, agency TEXT, agency_fee REAL, agent TEXT,
            cleanings TEXT, night_fare REAL, extras REAL, total_price REAL, payed REAL, balance REAL)
            '''
        )
        db.commit()
        
    app = PagesContainerApp()    
    app.title('Artesia Host Manager')

    home_app = HomePage(app.addTab("Home"))
    insert_app = InsertPageApp(cursor, app.addTab("New customer"))
    customers_app = CustomersPageApp(cursor, app.addTab("View customers"))
    db.commit()
    
    app.mainloop()    
    db.commit()

    cursor.execute('''SELECT * FROM customers''')
    all_customers = cursor.fetchall()

    for customer in all_customers:
        print(customer)
                           
