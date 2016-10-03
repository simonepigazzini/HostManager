#!/bin/python3

import os
import tkinter
import datetime

from tkinter.ttk import *
from collections import OrderedDict as odict

class InsertPageWidget():
    def __init__(self, column=0, row=0, label="", text=""):
        self.column = int(column)
        self.row = int(row)
        self.label = label
        self.text = text

        self.tk_label_str = tkinter.StringVar()
        self.tk_label = None
        self.tk_var = tkinter.StringVar()
        self.tk_widget = None

class InsertPageApp(tkinter.ttk.Frame):
    def __init__(self, db_cursor, parent=None):
        ###---create from parent class
        tkinter.ttk.Frame.__init__(self, parent)
        
        ###---objects    
        self.parent = parent
        self.dbc = db_cursor
        self.widget_insert_page = odict([("fullname",
                                          InsertPageWidget(row=0, column=0, label="Full name:", text="Enter customer full name")),
                                         ("arrival",
                                          InsertPageWidget(row=1, column=0, label="Arrival date:", text="dd/mm/year")),
                                         ("departure",
                                          InsertPageWidget(row=1, column=1, label="Departure date:", text="dd/mm/year")),
                                         ("agency",
                                          InsertPageWidget(row=2, column=0, label="Booking agancy:", text="agancy")),
                                         ("night_fare",
                                          InsertPageWidget(row=3, column=0, label="Night fare:", text="price")),
                                         ("total_price",
                                          InsertPageWidget(row=3, column=1, label="Total price:", text="total"))])
        ###---init single pages
        self.initialize_insert_page()

    #def initialize_global(self):

    def initialize_insert_page(self):
        """
        Initialize page for insert new customers.
        """
        
        ###---create widget holder
        self.grid()

        ###---enable automating resize
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ###---create page widget
        for key, widget in self.widget_insert_page.items():
            widget.tk_label = tkinter.Label(self, textvariable=widget.tk_label_str,
                                            anchor="w", fg="black", bg="#789696", font=("Helvatica", 11))
            widget.tk_label.grid(row=(widget.row*2), column=widget.column, columnspan=2, sticky='EW')
            widget.tk_label_str.set(widget.label)
            widget.tk_widget = tkinter.Entry(self, textvariable=widget.tk_var, font=("Helvatica", 11))
            widget.tk_widget.grid(row=(widget.row*2+1), column=widget.column, stick="EW")
            widget.tk_widget.config(fg="gray")
            widget.tk_widget.bind("<Button-1>", self.clear_callback)
            widget.tk_widget.bind("<Tab>", self.tab_callback)
            widget.tk_var.set(widget.text)

        insert_button = tkinter.Button(self, text=u"Insert")
        insert_button.grid(column=1, row=10)
        insert_button.bind("<Button-1>", self.insert_customer)
        insert_button.bind("<Enter>", self.insert_customer)

               
    def clear_callback(self, event):
        event.widget.delete(0, "end")        
        event.widget.config(fg="black")

    def tab_callback(self, event):
        next_widget = event.widget.tk_focusNext()
        next_widget.config(fg="black")
        next_widget.focus()

    def insert_customer(self, event):
        ###---get arrival date
        arrival_str = self.widget_insert_page["arrival"].tk_var.get()
        if len(arrival_str) == 10:
            arrival_date = datetime.datetime.strptime(arrival_str, "%d/%m/%Y")
        elif len(arrival_str) == 8:
            arrival_date = datetime.datetime.strptime(arrival_str, "%d/%m/%y")
        else:
            return
        ###---get departure date
        departure_str = self.widget_insert_page["departure"].tk_var.get()
        if len(departure_str) == 10:
            departure_date = datetime.datetime.strptime(departure_str, "%d/%m/%Y")
        elif len(departure_str) == 8:
            departure_date = datetime.datetime.strptime(departure_str, "%d/%m/%y")
        else:
            return
        
        new_customer = {key: widget.tk_var.get() for key, widget in self.widget_insert_page.items()}
        new_customer["nights"] = int((departure_date-arrival_date).days)
        self.dbc.execute(
        '''
        INSERT INTO Customers(fullname, arrival, departure, nights)
        VALUES(:fullname, :arrival, :departure, :nights)
        ''',
        new_customer)    
        db.commit()
