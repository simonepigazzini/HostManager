#!/bin/python3

import os
import re
import copy
import tkinter
import datetime
import time

from tkinter.ttk import *
from collections import OrderedDict as odict

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

class ViewPageEntry():
    def __init__(self, parent, column=0, row=0, label=""):
        self.parent = parent
        self.column = int(column)
        self.row = int(row)
        self.label = label
        
        self.tk_label_str = tkinter.StringVar()
        self.tk_label = tkinter.ttk.Label(self.parent, textvariable=self.tk_label_str, style="HM.TLabel")

        self.tk_var = tkinter.StringVar()
        self.tk_widget = tkinter.ttk.Entry(self.parent, textvariable=self.tk_var, font='TkDefaultFont 11', style="HMDefault.TEntry")

class CustomersPageApp():
    def __init__(self, db_cursor, parent=None):
        ###---story copy of db access cursor
        self.db_cursor = db_cursor
        
        ###---create from parent class
        self.parent = parent
        self.parent.bind("<Configure>", self.autoResize)

        self.widget_view_page = odict(
            [("id",
              ViewPageEntry(self.parent, column=0, label="ID number:")),
             ("fullname",
              ViewPageEntry(self.parent, column=1, label="Full name:")),
             ("building",
              ViewPageEntry(self.parent, column=2, label="Building:")),
             ("room",
              ViewPageEntry(self.parent, column=3, label="Room:")),
             ("arrival",
              ViewPageEntry(self.parent, column=4, label="Arrival date:")),
             ("departure",
              ViewPageEntry(self.parent, column=5, label="Departure date:")),
             ("nights",
              ViewPageEntry(self.parent, column=6, label="Nights:")),
             ("agency",
              ViewPageEntry(self.parent, column=7, label="Booking agancy:")),
             ("agency_fee",
              ViewPageEntry(self.parent, column=8, label="Agency fee:")),
              ("night_fare",
              ViewPageEntry(self.parent, column=9, label="Night fare:")),
             ("extras",
              ViewPageEntry(self.parent, column=10, label="Extras:")),
             ("total_price",
              ViewPageEntry(self.parent, column=11, label="Total price:")),
             ("payed",
              ViewPageEntry(self.parent, column=12, label="Payed:")),
             ("balance",
              ViewPageEntry(self.parent, column=13, label="Balance:"))
            ]
        )
        self.customers_widget_list = []

        ###---global static page widget
        ###---analyzed period begin
        self.period_begin_label_str = tkinter.StringVar()        
        self.period_begin_label = tkinter.ttk.Label(self.parent, textvariable=self.period_begin_label_str, style="HM.TLabel")
        self.period_begin_label.grid(row=0, column=0, columnspan=2)
        self.period_begin_label_str.set("Period begin:")
        self.period_begin_var = tkinter.StringVar()
        self.period_begin = tkinter.ttk.Entry(self.parent, textvariable=self.period_begin_var,
                                              font='TkDefaultFont 11', style="HMDefault.TEntry")
        self.period_begin.grid(row=0, column=2)
        self.period_begin_var.set(time.strftime("01/01/%Y"))
        ###---analyzed period end
        self.period_end_label_str = tkinter.StringVar()        
        self.period_end_label = tkinter.ttk.Label(self.parent, textvariable=self.period_end_label_str, style="HM.TLabel")
        self.period_end_label.grid(row=0, column=3, columnspan=2)
        self.period_end_label_str.set("Period end:")
        self.period_end_var = tkinter.StringVar()
        self.period_end = tkinter.ttk.Entry(self.parent, textvariable=self.period_end_var,
                                              font='TkDefaultFont 11', style="HMDefault.TEntry")
        self.period_end.grid(row=0, column=5)
        self.period_end_var.set(time.strftime("%d/%m/%Y"))
        ###---show button
        self.show_data_button = tkinter.ttk.Button(self.parent, text="Show_Data")
        self.show_data_button.grid(row=0, column=7)
        self.show_data_button.bind("<Button-1>", self.refreshData)
        self.show_data_button.bind("<Return>", self.refreshData)

        self.initializeViewPage(shift=1)

    def initializeViewPage(self, shift):

        tkinter.ttk.Style().map("HMDefault.TEntry",
                                foreground=[('active', 'gray'),
                                            ('disabled', 'black')],
                                background=[('active', 'white'),
                                            ('disabled', 'gray')])
        
        ###---create database widget
        self.data_starting_row = shift+1
        for key, widget in self.widget_view_page.items():
            widget.tk_label.grid(row=shift, column=widget.column, sticky="NWE")            
            widget.tk_label_str.set(widget.label)
            widget.tk_label.bind("<Configure>", self.wrapLabel)
            widget.tk_widget.grid(row=shift+1, column=widget.column, sticky="NWE")
            widget.tk_widget.config(state = "disabled")
            
        ###---scrollbar
        ybar = Scrollbar(self.parent)
        ybar.grid(column = self.parent.grid_size()[0]+1, row=shift+1, sticky="NSW")

    def wrapLabel(self, event):
        event.widget.configure(wraplength = event.widget.winfo_width()-10)

    def autoResize(self, event):
        for column in range(0, self.parent.grid_size()[0]-1):
            self.parent.columnconfigure(column, weight=1)
        # for row in range(0, self.parent.grid_size()[1]):
        #     self.parent.rowconfigure(row, weight=1)

    def refreshData(self, event):
        ###---fetch data
        if len(self.period_begin_var.get()) == 8:
            begin = datetime.datetime.strptime(self.period_begin_var.get(), '%d/%m/%y')
        elif len(self.period_begin_var.get()) == 10:
            begin = datetime.datetime.strptime(self.period_begin_var.get(), '%d/%m/%Y')
        if len(self.period_end_var.get()) == 8:
            end = datetime.datetime.strptime(self.period_end_var.get(), '%d/%m/%y')
        elif len(self.period_end_var.get()) == 10:
            end = datetime.datetime.strptime(self.period_end_var.get(), '%d/%m/%Y')
            
        self.db_cursor.execute('''SELECT * FROM customers WHERE arrival > ? AND departure < ?''', [begin, end])
        customers = self.db_cursor.fetchall()
    
        ###---create rows for fetched data
        widget_list = list(self.widget_view_page.items())
        for widget in self.customers_widget_list:
            widget.tk_widget.grid_forget()
        self.customers_widget_list = []
        field_sum = [0 for x in range(0, len(widget_list))]
        for row, customer in enumerate(customers):
            for index, data in enumerate(customer):
                widget = ViewPageEntry(self.parent, column=widget_list[index][1].column, label=widget_list[index][1].label)
                self.customers_widget_list.append(widget)
                self.customers_widget_list[-1].tk_widget.grid(row=self.data_starting_row+row, column=widget.column, sticky="NWE")
                self.customers_widget_list[-1].tk_widget.config(state = "disabled")
                self.customers_widget_list[-1].tk_var.set(data)
                field_sum[index] = field_sum[index]+float(data) if is_number(data) else None

        ###---compute sums
        
