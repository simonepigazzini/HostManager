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
    def __init__(self, parent, column=0, row=0, label="", function=None, **kwargs):
        self.parent = parent
        self.column = int(column)
        self.row = int(row)
        self.label = label
        self.function = function
        self.widget_width = len(self.label)+3
        
        self.tk_label = tkinter.ttk.Button(self.parent, text=label, width=self.widget_width)

        self.tk_var = tkinter.StringVar()
        self.tk_widget = tkinter.ttk.Entry(self.parent, width=self.widget_width, textvariable=self.tk_var,
                                           font='TkDefaultFont 11', style="HMDefault.TEntry")

        for option, value in kwargs.items():
            self.tk_label[option] = value
            self.tk_widget[option] = value

    def reloadLabel(self, parent=None):
        if not parent:
            parent=self.parent
        self.tk_label = tkinter.ttk.Button(parent, text=self.label, width=self.widget_width)

class ViewPageEntryId(ViewPageEntry):
    def __init__(self, parent, column=0, row=0, label="", function=None, **kwargs):
        ViewPageEntry.__init__(self, parent, column=column, row=row, label=label, function=function)

        self.tk_label = tkinter.ttk.Label(self.parent, text=label, width=self.widget_width)
        
class CustomersPageApp():
    def __init__(self, db_cursor, parent=None):
        ###---story copy of db access cursor        
        self.db_cursor = db_cursor
        ###---create from parent class
        self.parent = parent
        self.parent.bind("<Configure>", self.autoResize)

        ###---global static page widget
        ###---analyzed period begin
        query_frame = tkinter.ttk.Frame(self.parent)
        query_frame.pack(anchor="nw", fill="x")
        self.period_begin_label_str = tkinter.StringVar()
        self.period_begin_label = tkinter.ttk.Label(query_frame, textvariable=self.period_begin_label_str, style="HM.TLabel")
        self.period_begin_label.pack(side="left", anchor="nw", expand=True)
        self.period_begin_label_str.set("Period begin:")
        self.period_begin_var = tkinter.StringVar()
        self.period_begin_default = "01/01/%Y"
        self.period_begin = tkinter.ttk.Entry(query_frame, textvariable=self.period_begin_var,
                                              font='TkDefaultFont 11', style="HMDefault.TEntry")
        self.period_begin.pack(side="left", expand=True)
        self.period_begin_var.set(time.strftime(self.period_begin_default))
        self.period_begin.bind("<Button-1>", self.clickCallback)
        self.period_begin.bind("<Tab>", self.tabCallback)
        self.period_begin.bind("<Key>", self.dateCallback)
        ###---analyzed period end
        self.period_end_label_str = tkinter.StringVar()        
        self.period_end_label = tkinter.ttk.Label(query_frame, textvariable=self.period_end_label_str, style="HM.TLabel")
        self.period_end_label.pack(side="left", expand=True)
        self.period_end_label_str.set("Period end:")
        self.period_end_var = tkinter.StringVar()
        self.period_end_default = "01/01/%Y"
        self.period_end = tkinter.ttk.Entry(query_frame, textvariable=self.period_end_var,
                                              font='TkDefaultFont 11', style="HMDefault.TEntry")
        self.period_end.pack(side="left", expand=True)
        self.period_end_var.set(time.strftime(self.period_end_default))
        self.period_end.bind("<Button-1>", self.clickCallback)
        self.period_end.bind("<Tab>", self.tabCallback)
        self.period_end.bind("<Key>", self.dateCallback)
        ###---show button
        self.show_data_button = tkinter.ttk.Button(query_frame, text="Show_Data")
        self.show_data_button.pack(anchor="ne", side="right", expand=False)
        self.show_data_button.bind("<Button-1>", self.refreshData)
        self.show_data_button.bind("<Return>", self.refreshData)
        
        ###---create scrollable frame
        self.xscroll = tkinter.ttk.Scrollbar(self.parent, orient="horizontal")
        self.xscroll.pack(fill="x", side="bottom", expand=False)
        self.canvas = tkinter.Canvas(self.parent, xscrollcommand=self.xscroll.set)
        self.canvas.pack(side="bottom", fill="both", anchor="nw", expand=True)
        self.xscroll.config(command=self.canvas.xview)
        self.interior = tkinter.ttk.Frame(self.canvas)
        interior_id = self.canvas.create_window(0, 0, window=self.interior, anchor="nw")

        def syncFunction(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.interior.bind("<Configure>", syncFunction)

        ###---query frame separator
        query_separetor = tkinter.ttk.Separator(self.parent, orient="horizontal")
        query_separetor.pack(side="bottom", fill="x")
        
        ###---disabled field list
        self.disabled_fields_frame = tkinter.ttk.Frame(self.parent)
        self.disabled_fields_frame.pack(side="bottom", anchor="nw", fill="x")
        self.disabled_label = tkinter.ttk.Label(self.disabled_fields_frame, text="Disabled fields: ",
                                                width=len("Disabled fields: ")+3, style="HM.TLabel")
        self.disabled_label.pack(anchor="nw")
        disabled_separetor = tkinter.ttk.Separator(self.parent, orient="horizontal")
        disabled_separetor.pack(side="bottom", fill="x")

        ###---field widgets
        self.widget_view_page = odict(
            [("id",
              ViewPageEntryId(self.interior, column=0, label="ID number:")),
             ("fullname",
              ViewPageEntry(self.interior, column=1, label="Full name:")),
             ("building",
              ViewPageEntry(self.interior, column=2, label="Building:")),
             ("room",
              ViewPageEntry(self.interior, column=3, label="Room:")),
             ("arrival",
              ViewPageEntry(self.interior, column=4, label="Arrival date:")),
             ("departure",
              ViewPageEntry(self.interior, column=5, label="Departure date:")),
             ("nights",
              ViewPageEntry(self.interior, column=6, label="Nights:")),
             ("agency",
              ViewPageEntry(self.interior, column=7, label="Booking agancy:")),
             ("agency_fee",
              ViewPageEntry(self.interior, column=8, label="Agency fee:")),
              ("night_fare",
              ViewPageEntry(self.interior, column=9, label="Night fare:")),
             ("extras",
              ViewPageEntry(self.interior, column=10, label="Extras:")),
             ("total_price",
              ViewPageEntry(self.interior, column=11, label="Total price:")),
             ("payed",
              ViewPageEntry(self.interior, column=12, label="Payed:")),
             ("balance",
              ViewPageEntry(self.interior, column=13, label="Balance:")),
             ("iva",
              ViewPageEntry(self.interior, column=14, label="IVA (22%):", function=self.computeIVA)),
            ]
        )
        self.customers_widget_list = []
        self.disabled_fields = []

        self.initializeViewPage(shift=1)
        
    def initializeViewPage(self, shift):

        tkinter.ttk.Style().map("HMDefault.TEntry",
                                foreground=[('active', 'gray'),
                                            ('disabled', 'black')],
                                background=[('active', 'white'),
                                            ('disabled', 'gray')])
        
        ###---create database widget
        self.data_next_row = shift+1
        self.placeFieldsLabel(shift=shift)

    def placeFieldsLabel(self, shift):
        column = 0
        for key, widget in self.widget_view_page.items():
            if key in self.disabled_fields:
                widget.tk_label.pack_forget()
                widget.reloadLabel(parent=self.disabled_fields_frame)
                widget.tk_label.pack(side="left")
                widget.tk_label.bind("<Button-1>", self.showField)
            elif key != "id":
                widget.tk_label.grid_forget()
                widget.reloadLabel()
                widget.tk_label.grid(row=shift, column=column, sticky="NWE")                
                widget.tk_label.bind("<Button-1>", self.hideField)
                column += 1
            else:
                widget.tk_label.grid(row=shift, column=column, sticky="NWE")
                column += 1

        self.widget_view_page_item = odict([(item.tk_label, item) for key, item in self.widget_view_page.items()])
        self.widget_view_page_name = odict([(item.tk_label, key) for key, item in self.widget_view_page.items()])
        
    def hideField(self, event):
        event.widget.grid_forget()
        self.disabled_fields.append(self.widget_view_page_name[event.widget])
        self.placeFieldsLabel(shift=1)
        self.refreshData(event)

    def showField(self, event):
        event.widget.pack_forget()
        self.disabled_fields.remove(self.widget_view_page_name[event.widget])
        self.placeFieldsLabel(shift=1)
        self.refreshData(event)
        
    def wrapLabel(self, event):
        event.widget.configure(wraplength = event.widget.winfo_width()-10)

    def autoResize(self, event):
        for column in range(0, self.parent.grid_size()[0]):
            self.parent.columnconfigure(column, weight=1)

    def computeIVA(self):
        index = (int(self.widget_view_page['total_price'].column) + len(list(self.widget_view_page.items()))*
                 int(len(self.customers_widget_list)/len(list(self.widget_view_page.items()))-1))
        return float(self.customers_widget_list[index].tk_var.get())*0.22
        
    def refreshData(self, event):
        next_row = self.data_next_row
        
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
            widget.tk_widget.grid_remove()
        self.customers_widget_list = []
        field_sum = [0 for x in range(0, len(widget_list))]
        for row, customer in enumerate(customers):
            next_column = 0
            for index, data in enumerate(customer):
                if widget_list[index][0] in self.disabled_fields:
                    continue
                widget = ViewPageEntry(self.interior, column=widget_list[index][1].column, label=widget_list[index][1].label)
                self.customers_widget_list.append(widget)
                self.customers_widget_list[-1].tk_widget.grid(row=next_row, column=next_column, sticky="NWE")
                self.customers_widget_list[-1].tk_widget.config(state = "disabled")
                self.customers_widget_list[-1].tk_var.set(data)
                ###---compute sums if applicable
                field_sum[index] = field_sum[index]+float(data) if is_number(data) else None
                next_column += 1
            ###---compute fields that are not stored in the db
            for name, field in [(name, widget) for name, widget in self.widget_view_page.items() if widget.function != None]:
                if name in self.disabled_fields:
                    continue
                widget = ViewPageEntry(self.interior, column=field.column, label=field.label, function=field.function)
                self.customers_widget_list.append(widget)                
                self.customers_widget_list[-1].tk_widget.grid(row=next_row, column=next_column, sticky="NWE")
                self.customers_widget_list[-1].tk_widget.config(state = "disabled")
                self.customers_widget_list[-1].tk_var.set(widget.function())
                ###---compute sums if applicable
                field_sum[widget.column] += widget.function()
                next_column += 1
            next_row += 1

        ###---display sums
        if len(customers) > 0:
            self.sum_line = tkinter.ttk.Separator(self.interior, orient="horizontal")
            self.sum_line.grid(row=next_row, columnspan=len(widget_list), sticky="EW")
            next_row += 1
            next_column = 0
            for index, field in enumerate(widget_list):
                if field[0] in self.disabled_fields:
                    continue
                widget = ViewPageEntry(self.interior, column=field[1].column, label=field[1].label)
                self.customers_widget_list.append(widget)
                self.customers_widget_list[-1].tk_widget.grid(row=next_row, column=next_column, sticky="NWE")
                self.customers_widget_list[-1].tk_widget.config(state = "disabled")
                value = field_sum[index] if field_sum[index] else ""
                value = "Total:" if widget.column == 0 else value
                self.customers_widget_list[-1].tk_var.set(value)
                next_column += 1
            
    def dateCallback(self, event):
        value = event.char
        widget = self.period_begin if event.widget == self.period_begin else self.period_end
        default_entry = self.period_begin_default if event.widget == self.period_begin else self.period_end_default
        entry = self.period_begin_var.get() if event.widget == self.period_begin else self.period_end_var.get()
        special_key = event.keysym in ['Left', 'Right', 'BackSpace', 'Delete', 'Cancel']
        if value not in "01233456789/" and not special_key:
            return("break")
        if entry == time.strftime(default_entry):
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
        
