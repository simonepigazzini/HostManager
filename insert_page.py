#!/bin/python3

import os
import re
import copy
import tkinter
import datetime

from tkinter import messagebox
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
        self.is_good_flag = False
        
        self.tk_label_str = tkinter.StringVar()
        self.tk_label = tkinter.ttk.Label(self.parent, textvariable=self.tk_label_str, style="HM.TLabel")

    def isModified(self):
        return (self.tk_var.get() != self.text and self.tk_var.get() != "")

class InsertPageEntry(InsertPageWidget):
    def __init__(self, parent, column=0, row=0, label="", text="", callback_map={}, **kwargs):
        ###---call base class init fuction
        InsertPageWidget.__init__(self, parent, column=column, row=row, label=label, text=text, callback_map=callback_map)
        
        self.tk_var = tkinter.StringVar()
        self.tk_widget = tkinter.ttk.Entry(self.parent, textvariable=self.tk_var, font='TkDefaultFont 11', style="HMDefault.TEntry")

        for option, value in kwargs.items():
            self.tk_widget[option] = value
        
class InsertPageEntryMenu(InsertPageWidget):
    def __init__(self, parent, column=0, row=0, label="", options=[], callback_map={}, **kwargs):
        ###---call base class init fuction
        InsertPageWidget.__init__(self, parent, column=column, row=row, label=label, text=options[0], callback_map=callback_map)
        self.is_good_flag = True
        
        self.tk_var = tkinter.StringVar()
        self.tk_widget = tkinter.ttk.OptionMenu(self.parent, self.tk_var, options[0], *options, style="HMDefault.TMenubutton")
        
class InsertPageApp():
    def __init__(self, db_cursor, parent=None):
        ###---create from parent class
        self.parent = parent
        self.parent.bind("<Configure>", self.autoResize)

        ###---set style
        tkinter.ttk.Style().configure("HM.TLabel", anchor="w", foreground="black")
        tkinter.ttk.Style().configure("HMError.TLabel", anchor="w", foreground="red")
        tkinter.ttk.Style().configure("HMDefault.TEntry", foreground="gray", borderwidth=5, relief="flat")
        tkinter.ttk.Style().configure("HMInsert.TEntry", foreground="black", borderwidth=5, relief="flat")
        tkinter.ttk.Style().configure("HMDefault.TMenubutton", background="white", borderwidth=2, relief="flat")
        
        ###---data
        self.stay_info = {}
        self.rooms = {"Villa Maria": ["Double", "Triple", "All"], "Palazzo Iargia" : ["Rosa", "Blu", "Bianca"]}
        
        ###---objects    
        self.dbc = db_cursor
        std_entry_callbacks = {"<Button-1>": self.clickCallback,
                               "<Tab>": self.tabCallback,
                               "<Key>": self.clearCallback}
        std_menu_callbacks = {}
        self.widget_insert_page = odict(
            [("fullname",
              InsertPageEntry(self.parent, row=0, column=0, label="Full name:", text="Enter customer full name",
                              callback_map=std_entry_callbacks)),
             ("building",
              InsertPageEntryMenu(self.parent, row=1, column=0, label="Building:", options=["Villa Maria", "Palazzo Iargia"])),
             ("room",
              InsertPageEntryMenu(self.parent, row=1, column=1, label="Room:",
                                  options=self.rooms["Villa Maria"])),
             ("arrival",
              InsertPageEntry(self.parent, row=2, column=0, label="Arrival date:", text="dd/mm/year",
                              callback_map=std_entry_callbacks)),
             ("departure",
              InsertPageEntry(self.parent, row=2, column=1, label="Departure date:", text="dd/mm/year",
                              callback_map=std_entry_callbacks)),
             ("nights",
              InsertPageEntry(self.parent, row=2, column=2, label="Nights:", text="",
                              callback_map=std_entry_callbacks, state="disable")),              
             ("agency",
              InsertPageEntryMenu(self.parent, row=3, column=0, label="Booking agancy:",
                                  options=["None", "Booking", "Airbnb", "Homeaway", "Homeholidays", "Expedia"])),
             ("agency_fee",
              InsertPageEntry(self.parent, row=3, column=1, label="Agency fee:", text="fee (euro)", callback_map=std_entry_callbacks)),
             ("night_fare",
              InsertPageEntry(self.parent, row=4, column=0, label="Night fare:", text="price", callback_map=std_entry_callbacks)),
             ("extras",
              InsertPageEntry(self.parent, row=4, column=1, label="Extras:", text="extras total price", callback_map=std_entry_callbacks)),
             ("total_price",
              InsertPageEntry(self.parent, row=4, column=2, label="Total price:", text="total", callback_map=std_entry_callbacks)),
             ("payed",
              InsertPageEntry(self.parent, row=5, column=2, label="Payed:", text="0", callback_map=std_entry_callbacks)),
             ("balance",
              InsertPageEntry(self.parent, row=6, column=2, label="Balance:", text="", callback_map=std_entry_callbacks, state="disable")),
            ]
        )
        self.widget_insert_page["fullname"].callback_map["<FocusOut>"] = self.checkEmptyField
        self.widget_insert_page["arrival"].callback_map["<FocusOut>"] = self.validateDate
        self.widget_insert_page["arrival"].callback_map["<Key>"] = self.dateCallback
        self.widget_insert_page["departure"].callback_map["<FocusOut>"] = self.validateDate
        self.widget_insert_page["departure"].callback_map["<Key>"] = self.dateCallback
        self.widget_insert_page["agency_fee"].callback_map["<FocusOut>"] = self.checkFeeValidity
        self.widget_insert_page["agency_fee"].callback_map["<Key>"] = self.priceCallback
        self.widget_insert_page["night_fare"].callback_map["<Key>"] = self.priceCallback
        self.widget_insert_page["extras"].callback_map["<Key>"] = self.priceCallback
        self.widget_insert_page["total_price"].callback_map["<Key>"] = self.priceCallback
        self.widget_insert_page["payed"].callback_map["<Key>"] = self.priceCallback
        self.widget_insert_page["agency_fee"].callback_map["<FocusOut>"] = lambda event : self.checkAccounting()
        self.widget_insert_page["night_fare"].callback_map["<FocusOut>"] = lambda event : self.checkAccounting()
        self.widget_insert_page["extras"].callback_map["<FocusOut>"] = lambda event : self.checkAccounting()
        self.widget_insert_page["total_price"].callback_map["<FocusOut>"] = lambda event : self.checkAccounting()
        self.widget_insert_page["payed"].callback_map["<FocusOut>"] = lambda event : self.checkAccounting()
        
        ###---init single pages
        self.initializeInsertPage()
        
    #def initialize_global(self):

    def initializeInsertPage(self):
        """
        Initialize page for insert new customers.
        """
    
        tkinter.ttk.Style().map("HMDefault.TEntry",
                                foreground=[('active', 'gray'),
                                            ('disabled', 'black')],
                                background=[('active', 'white'),
                                            ('disabled', 'gray')])
        
        ###---create page widget
        for key, widget in self.widget_insert_page.items():
            widget.tk_label.grid(row=(widget.row*2), column=widget.column, columnspan=2, sticky="NWES")
            widget.tk_label_str.set(widget.label)
            widget.tk_widget.grid(row=(widget.row*2+1), column=widget.column, sticky="NWES")
            widget.tk_var.set(widget.text)
            for event, call in widget.callback_map.items():
                widget.tk_widget.bind(event, call)

        self.insert_button = tkinter.ttk.Button(self.parent, text="Insert")
        self.insert_button.grid(columnspan=self.parent.grid_size()[0], column=0, row=self.parent.grid_size()[1])
        self.insert_button.bind("<Button-1>", self.tryInsertCustomer)
        self.insert_button.bind("<Return>", self.tryInsertCustomer)

        ###---track option menu variables
        self.widget_insert_page["building"].tk_var.trace('w', self.trimRoomsField)
        
        ###---define reverse mapping widget -> InsertPageEntry
        self.widget_insert_page_item = odict([(item.tk_widget, item) for key, item in self.widget_insert_page.items()])
        self.widget_insert_page_keys = odict([(item.tk_widget, key) for key, item in self.widget_insert_page.items()])
        
    def clearCallback(self, event):
        if self.widget_insert_page_item[event.widget].tk_var.get() == self.widget_insert_page_item[event.widget].text:
            event.widget.delete(0, "end")        
            event.widget.config(style="HMInsert.TEntry")

    def priceCallback(self, event):
        value = event.char
        entry = self.widget_insert_page_item[event.widget].tk_var.get()
        special_key = event.keysym in ['Left', 'Right', 'BackSpace', 'Delete', 'Cancel']
        if value not in "01233456789\." and not special_key:
            return("break")
        if not self.widget_insert_page_item[event.widget].isModified():
            event.widget.delete(0, "end")        
            event.widget.config(style="HMInsert.TEntry")
            
    def dateCallback(self, event):
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
            event.widget.tk_focusNext().focus()
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
            self.widget_insert_page_item[event.widget].is_good_flag = False
        else:
            self.widget_insert_page_item[event.widget].tk_label.config(style="HM.TLabel")
            self.widget_insert_page_item[event.widget].is_good_flag = True
            
        return("break")

    def checkFeeValidity(self, event):
        """
        like checkEmptyField but allow empty field if <agency> field is None
        """

        if self.widget_insert_page["agency"].tk_var.get() != "None":
            return self.checkEmptyField(event)
    
    def trimRoomsField(self, *args):
        """
        Trim room selection based on chosen building:
        - the old "room" widget is deleted
        - a new one is created
        """

        options = self.rooms[self.widget_insert_page["building"].tk_var.get()]
        room_obj = self.widget_insert_page["room"]
        room_obj.tk_widget = tkinter.ttk.OptionMenu(room_obj.parent, room_obj.tk_var,
                                                    options[0], *options, style="HMDefault.TMenubutton")
        room_obj.tk_widget.grid(row=(room_obj.row*2+1), column=room_obj.column, sticky="NWES")
        room_obj.tk_var.set(options[0])
        
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
                    self.widget_insert_page_item[event.widget].is_good_flag = True
                    break
                except ValueError:
                    self.widget_insert_page_item[event.widget].tk_label.config(style="HMError.TLabel")
                    self.widget_insert_page_item[event.widget].is_good_flag = False
                    return("break")
        else:
            while True:
                try:
                    self.stay_info[self.widget_insert_page_keys[event.widget]] = datetime.datetime.strptime(date, "%d/%m/%y")
                    self.widget_insert_page_item[event.widget].tk_label.config(style="HM.TLabel")
                    self.widget_insert_page_item[event.widget].is_good_flag = True
                    break
                except ValueError:
                    self.widget_insert_page_item[event.widget].tk_label.config(style="HMError.TLabel")
                    self.widget_insert_page_item[event.widget].is_good_flag = False
                    return("break")

        if "arrival" in self.stay_info.keys() and "departure" in self.stay_info.keys():
            self.stay_info["nights"] = int((self.stay_info["departure"]-self.stay_info["arrival"]).days)
            if self.stay_info["nights"] < 1:
                self.widget_insert_page["arrival"].tk_label.config(style="HMError.TLabel")
                self.widget_insert_page["departure"].tk_label.config(style="HMError.TLabel")
                self.widget_insert_page["arrival"].is_good_flag = False
                self.widget_insert_page["departure"].is_good_flag = False
            else:
                self.widget_insert_page["arrival"].tk_label.config(style="HM.TLabel")
                self.widget_insert_page["departure"].tk_label.config(style="HM.TLabel")
                self.widget_insert_page["nights"].tk_var.set(self.stay_info["nights"])
                self.widget_insert_page["arrival"].is_good_flag = True
                self.widget_insert_page["departure"].is_good_flag = True
                self.widget_insert_page["nights"].is_good_flag = True

    def checkAccounting(self):
        """
        Check night fare, extra services and total price and compute missing fields if needed
        """

        if self.widget_insert_page["agency"].tk_var.get() == "None":
            self.widget_insert_page["agency_fee"].tk_var.set("0")
            self.widget_insert_page["agency_fee"].tk_widget.config(style="HM.TEntry")
            self.widget_insert_page["agency_fee"].is_good_flag = True

        nights_widget = self.widget_insert_page["nights"]
        extras_widget = self.widget_insert_page["extras"]
        fare_widget = self.widget_insert_page["night_fare"]
        total_widget = self.widget_insert_page["total_price"]
        payed_widget = self.widget_insert_page["payed"]
        balance_widget = self.widget_insert_page["balance"]

        if not extras_widget.isModified():
            extras_widget.tk_var.set(0)
        
        if nights_widget.is_good_flag:
            if fare_widget.isModified() and not total_widget.isModified():
                total_widget.tk_var.set(float(fare_widget.tk_var.get())*int(nights_widget.tk_var.get())
                                        + float(extras_widget.tk_var.get()))
            elif not fare_widget.isModified() and total_widget.isModified():
                fare_widget.tk_var.set(float(total_widget.tk_var.get()) - float(extras_widget.tk_var.get())
                                       / int(nights_widget.tk_var.get()))
            elif not fare_widget.isModified() and not total_widget.isModified():
                return [fare_widget, total_widget]

            balance_widget.tk_var.set(float(total_widget.tk_var.get())-float(payed_widget.tk_var.get()))
            extras_widget.is_good_flag = True
            fare_widget.is_good_flag = True
            total_widget.is_good_flag = True
            payed_widget.is_good_flag = True
            balance_widget.is_good_flag = True            
        
    def tryInsertCustomer(self, event):
        """
        Parse information on new customer and check field validity
        """
          
        bad_fields = []
        bad_fields.append(self.checkAccounting())
        for field, widget in self.widget_insert_page.items():
            if not widget.is_good_flag:
                bad_fields.append(widget)

        bad_fields = [field for field in bad_fields if field is not None]
        if len(bad_fields) != 0:
            message = "Check this fields: \n"
            for field in bad_fields:
                message += " - "+field.tk_label_str.get()+"\n"
            tkinter.messagebox.showerror("Wrong customer parameters", message, parent=self.parent)
        elif tkinter.messagebox.askokcancel("Please confirm", "Insert new customer?", parent=self.parent):
            self.insertCustomer()
            
        return("break")
            
    def insertCustomer(self):        
        new_customer = {key: widget.tk_var.get() for key, widget in self.widget_insert_page.items()}
        ###---convert dates string into datetime objects
        if len(new_customer['arrival']) == 8:
            new_customer['arrival'] = datetime.datetime.strptime(new_customer['arrival'], '%d/%m/%y').date()
        elif len(new_customer['arrival']) == 10:
            new_customer['arrival'] = datetime.datetime.strptime(new_customer['arrival'], '%d/%m/%Y').date()
        if len(new_customer['departure']) == 8:
            new_customer['departure'] = datetime.datetime.strptime(new_customer['departure'], '%d/%m/%y').date()
        elif len(new_customer['departure']) == 10:
            new_customer['departure'] = datetime.datetime.strptime(new_customer['departure'], '%d/%m/%Y').date()
            
        self.dbc.execute(
        '''
        INSERT INTO Customers(fullname, building, room, arrival, departure, nights, agency, 
        agency_fee, night_fare, extras, total_price, payed, balance)
        VALUES(:fullname, :building, :room, :arrival, :departure, :nights, :agency,
        :agency_fee, :night_fare, :extras, :total_price, :payed, :balance)
        ''',
        new_customer)    

    def autoResize(self, event):
        for column in range(0, self.parent.grid_size()[0]-1):
            self.parent.columnconfigure(column, weight=1)
        for row in range(0, self.parent.grid_size()[1]):
            self.parent.rowconfigure(row, weight=1)
