#!/bin/python3

import os
import sqlite3
import tkinter
import datetime

from tkinter.ttk import *
from collections import OrderedDict as odict

from pages_container import *
from insert_page import *
        
if __name__ == "__main__":

    db = sqlite3.connect('data/customer.db')
    cursor = db.cursor()
    
    cursor.execute(
        '''
        SELECT * FROM sqlite_master WHERE name ='Customers' and type='table'
        '''
    )
    if not cursor.fetchone():
        cursor.execute(
            '''
            CREATE TABLE Customers(id INTEGER PRIMARY KEY, fullname TEXT, agency TEXT, nights INTEGER,
            arrival TEXT, departure TEXT)
            '''
        )
        db.commit()

    app = PagesContainerApp()    
    app.title('Artesia Host Manager')

    fake = app.new_page("Fake")
    insert_app = InsertPageApp(cursor, parent=app.new_page("New customer"))
    
    app.mainloop()    


cursor.execute('''SELECT fullname, arrival, departure, agency, nights FROM customers''')
all_customers = cursor.fetchall()

for customer in all_customers:
    print(customer)
                           
