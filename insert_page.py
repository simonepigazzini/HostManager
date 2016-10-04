#!/bin/python3

import os
import re
import copy
import tkinter
import datetime

from tkinter.ttk import *
from collections import OrderedDict as odict

class InsertPageWidget():
    def __init__(self, parent, column=0, row=0, label="", text="", callback_map={}):
        self.parent = parent
        self.column = int(column)
        self.row = int(row)
        self.label = label
        self.text = text
        self.callback_map = copy.copy(callback_map)

        self.tk_label_str = tkinter.StringVar()
        self.tk_label = tkinter.ttk.Label(self.parent, textvariable=self.tk_label_str, style="HM.TLabel")

    def isModified(self):
        return self.tk_var.get() != self.text

class InsertPageEntry(InsertPageWidget):
    def __init__(self, parent, column=0, row=0, label="", text="", callback_map={}, **kwargs):
        ###---call base class init fuction
        InsertPageWidget.__init__(self, parent, column=column, row=row, label=label, text=text, callback_map=callback_map)
        
        self.tk_var = tkinter.StringVar()
        self.tk_widget = tkinter.ttk.Entry(self.parent, textvariable=self.tk_var, style="HMDefault.TEntry")        

        for option, value in kwargs.items():
            self.tk_widget[option] = value
        
class InsertPageEntryMenu(InsertPageWidget):
    def __init__(self, parent, column=0, row=0, label="", options=[], callback_map={}, **kwargs):
        ###---call base class init fuction
        InsertPageWidget.__init__(self, parent, column=column, row=row, label=label, text=options[0], callback_map=callback_map)
        
        self.tk_var = tkinter.StringVar()
        self.tk_widget = tkinter.ttk.OptionMenu(self.parent, self.tk_var, options[0], *options, style="HMDefault.TMenubutton")
        
class InsertPageApp(tkinter.ttk.Frame):
    def __init__(self, db_cursor, parent=None):
        ###---create from parent class
        tkinter.ttk.Frame.__init__(self, parent)

        ###---data
        self.stay_info = {}
        
        ###---objects    
        self.parent = parent
        self.dbc = db_cursor
        std_entry_callbacks = {"<Button-1>": self.clickCallback,
                               "<Tab>": self.tabCallback,
                               "<Key>": self.clearCallback}
        std_menu_callbacks = {}
        self.widget_insert_page = odict(
            [("fullname",
              InsertPageEntry(self, row=0, column=0, label="Full name:", text="Enter customer full name",
                              callback_map=std_entry_callbacks)),
             ("arrival",
              InsertPageEntry(self, row=1, column=0, label="Arrival date:", text="dd/mm/year",
                              callback_map=std_entry_callbacks)),
             ("departure",
              InsertPageEntry(self, row=1, column=1, label="Departure date:", text="dd/mm/year",
                              callback_map=std_entry_callbacks)),
             ("nights",
              InsertPageEntry(self, row=1, column=2, label="Nights:", text="",
                              callback_map=std_entry_callbacks, state="disable")),              
             ("agency",
              InsertPageEntryMenu(self, row=2, column=0, label="Booking agancy:",
                                  options=["None", "Booking", "Airbnb", "Homeaway", "Homeholidays", "Expedia"])),
             ("agency_fee",
              InsertPageEntry(self, row=2, column=1, label="Agency fee:", text="fee (euro)", callback_map=std_entry_callbacks)),
             ("night_fare",
              InsertPageEntry(self, row=3, column=0, label="Night fare:", text="price", callback_map=std_entry_callbacks)),
             ("extras",
              InsertPageEntry(self, row=3, column=1, label="Extras:", text="extras total price", callback_map=std_entry_callbacks)),
             ("total_price",
              InsertPageEntry(self, row=3, column=2, label="Total price:", text="total", callback_map=std_entry_callbacks))]
        )
        self.widget_insert_page["fullname"].callback_map["<FocusOut>"] = self.checkEmptyField
        self.widget_insert_page["arrival"].callback_map["<FocusOut>"] = self.validateDate
        self.widget_insert_page["arrival"].callback_map["<Key>"] = self.keyCallback
        self.widget_insert_page["departure"].callback_map["<FocusOut>"] = self.validateDate
        self.widget_insert_page["departure"].callback_map["<Key>"] = self.keyCallback
        self.widget_insert_page["agency_fee"].callback_map["<FocusOut>"] = self.checkEmptyField
        
        ###---init single pages
        self.initializeInsertPage()
        
    #def initialize_global(self):

    def initializeInsertPage(self):
        """
        Initialize page for insert new customers.
        """
        
        ###---create widget holder
        self.grid()

        ###---enable automating resize
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ###---set style
        tkinter.ttk.Style().configure("HM.TLabel", anchor="w", foreground="black")
        tkinter.ttk.Style().configure("HMError.TLabel", anchor="w", foreground="red")
        tkinter.ttk.Style().configure("HMDefault.TEntry", foreground="gray", borderwidth=5, relief="flat")
        tkinter.ttk.Style().configure("HMInsert.TEntry", foreground="black", borderwidth=5, relief="flat")
        tkinter.ttk.Style().configure("HMDefault.TMenubutton", background="white", borderwidth=0, relief="flat")

        tkinter.ttk.Style().map("HMDefault.TEntry",
                                foreground=[('active', 'gray'),
                                            ('disabled', 'black')],
                                background=[('active', 'white'),
                                            ('disabled', 'gray')])
        
        ###---create page widget
        for key, widget in self.widget_insert_page.items():
            widget.tk_label.grid(row=(widget.row*2), column=widget.column, columnspan=2, sticky='EW')
            widget.tk_label_str.set(widget.label)
            widget.tk_widget.grid(row=(widget.row*2+1), column=widget.column, stick="EW")
            widget.tk_var.set(widget.text)
            for event, call in widget.callback_map.items():
                widget.tk_widget.bind(event, call)

        insert_button = tkinter.ttk.Button(self, text="Insert")
        insert_button.grid(columnspan=3, column=0, row=10,)
        insert_button.bind("<Button-1>", self.insertCustomer)
        insert_button.bind("<Return>", self.insertCustomer)

        ###---define reverse mapping widget -> InsertPageEntry
        self.widget_insert_page_item = odict([(item.tk_widget, item) for key, item in self.widget_insert_page.items()])
        self.widget_insert_page_keys = odict([(item.tk_widget, key) for key, item in self.widget_insert_page.items()])
        
    def clearCallback(self, event):
        if self.widget_insert_page_item[event.widget].tk_var.get() == self.widget_insert_page_item[event.widget].text:
            event.widget.delete(0, "end")        
            event.widget.config(style="HMInsert.TEntry")

    def keyCallback(self, event):
        value = event.char
        entry = self.widget_insert_page_item[event.widget].tk_var.get()
        special_key = event.keysym in ['Left', 'Right', 'BackSpace', 'Delete', 'Cancel']
        if value not in "01233456789/" and not special_key:
            return("break")
        if not self.widget_insert_page_item[event.widget].isModified():
            event.widget.delete(0, "end")        
            event.widget.config(style="HMInsert.TEntry")
        elif (len(entry) == 2 or len(entry) == 5) and value != '/' and not special_key:
            event.widget.insert("insert", '/')
        elif len(entry) == 10 and not special_key:
            return("break")
            
    def tabCallback(self, event):
        event.widget.tk_focusNext().focus()

    def clickCallback(self, event):        
        event.widget.focus()
        event.widget.select_range(0, "end")
        return("break")

    def checkEmptyField(self, event):
        """
        Validate field: check if field has been filled
        """
        
        field_str = self.widget_insert_page_item[event.widget].tk_var.get()
        if field_str == "" or not self.widget_insert_page_item[event.widget].isModified():
            self.widget_insert_page_item[event.widget].tk_var.set(self.widget_insert_page_item[event.widget].text)
            self.widget_insert_page_item[event.widget].tk_label.config(style="HMError.TLabel")
        else:
            self.widget_insert_page_item[event.widget].tk_label.config(style="HM.TLabel")
            
        return("break")
            
    def validateDate(self, event):
        """
        Validate date format. Allowed format: dd/mm/yyyy or dd/mm/yy
        """

        date = self.widget_insert_page_item[event.widget].tk_var.get()
        if len(date) == 10:
            while True:
                try:
                    self.stay_info[self.widget_insert_page_keys[event.widget]] = datetime.datetime.strptime(date, "%d/%m/%Y")
                    self.widget_insert_page_item[event.widget].tk_label.config(style="HM.TLabel")
                    break
                except ValueError:
                    self.widget_insert_page_item[event.widget].tk_label.config(style="HMError.TLabel")
                    return("break")
        else:
            while True:
                try:
                    self.stay_info[self.widget_insert_page_keys[event.widget]] = datetime.datetime.strptime(date, "%d/%m/%y")
                    self.widget_insert_page_item[event.widget].tk_label.config(style="HM.TLabel")
                    break
                except ValueError:
                    self.widget_insert_page_item[event.widget].tk_label.config(style="HMError.TLabel")
                    return("break")

        if "arrival" in self.stay_info.keys() and "departure" in self.stay_info.keys():
            self.stay_info["nights"] = int((self.stay_info["departure"]-self.stay_info["arrival"]).days)
            if self.stay_info["nights"] < 1:
                self.widget_insert_page["arrival"].tk_label.config(style="HMError.TLabel")
                self.widget_insert_page["departure"].tk_label.config(style="HMError.TLabel")
            else:
                self.widget_insert_page["arrival"].tk_label.config(style="HM.TLabel")
                self.widget_insert_page["departure"].tk_label.config(style="HM.TLabel")
                self.widget_insert_page["nights"].tk_var.set(self.stay_info["nights"])
            
    def checkInsertCustomer(self, event):
        """
        Parse information on new customer and check field validity
        """
        return
        # self.validate_date(self.widget_insert_page["arrival"].tk_var.get())
        # self.validate_date(self.widget_insert_page["departure"].tk_var.get())        
        
    def insertCustomer(self, event):        
        new_customer = {key: widget.tk_var.get() for key, widget in self.widget_insert_page.items()}
        self.dbc.execute(
        '''
        INSERT INTO Customers(fullname, arrival, departure, nights, agency)
        VALUES(:fullname, :arrival, :departure, :nights, :agency)
        ''',
        new_customer)    
