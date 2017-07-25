#!/bin/python3

import os
import re
import copy
import tkinter
import datetime
import time

from PIL import Image, ImageTk
from tkinter import messagebox
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
        self.period_end_default = datetime.datetime.strftime(datetime.datetime.now(), "%d/%m/%Y")
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
        self.show_data_button.bind("<Button-1>", self.showData)
        self.show_data_button.bind("<Return>", self.showData)
        
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

        ###---filters frame
        self.filters_frame = tkinter.ttk.Frame(self.parent)
        self.filters_frame.pack(side="bottom", anchor="nw", fill="x")
        self.filters_label = tkinter.ttk.Label(self.filters_frame, text="Filters: ",
                                                  width=len("Filters: ")+3, style="HM.TLabel")
        self.filters_label.pack(anchor="nw")
        filters_separetor = tkinter.ttk.Separator(self.parent, orient="horizontal")
        filters_separetor.pack(side="bottom", fill="x")        
        
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
              {"dummy": ViewPageEntryId(self.interior, column=0, label="ID number:")}),
             ("fullname",
              {"dummy": ViewPageEntry(self.interior, column=1, label="Full name:")}),
             ("building",
              {"dummy": ViewPageEntry(self.interior, column=2, label="Building:")}),
             ("room",
              {"dummy": ViewPageEntry(self.interior, column=3, label="Room:")}),
             ("arrival",
              {"dummy": ViewPageEntry(self.interior, column=4, label="Arrival date:")}),
             ("departure",
              {"dummy": ViewPageEntry(self.interior, column=5, label="Departure date:")}),
             ("nights",
              {"dummy": ViewPageEntry(self.interior, column=6, label="Nights:")}),
             ("agency",
              {"dummy": ViewPageEntry(self.interior, column=7, label="Booking agancy:")}),
             ("agency_fee",
              {"dummy": ViewPageEntry(self.interior, column=8, label="Agency fee:")}),
             ("agent",
              {"dummy": ViewPageEntry(self.interior, column=9, label="Agent:")}),
             ("cleanings",
              {"dummy": ViewPageEntry(self.interior, column=10, label="Cleaner:")}),
             ("night_fare",
               {"dummy": ViewPageEntry(self.interior, column=11, label="Night fare:")}),
             ("extras",
              {"dummy": ViewPageEntry(self.interior, column=12, label="Extras:")}),
             ("total_price",
              {"dummy": ViewPageEntry(self.interior, column=13, label="Total price:")}),
             ("payed",
              {"dummy": ViewPageEntry(self.interior, column=14, label="Payed:")}),
             ("balance",
              {"dummy": ViewPageEntry(self.interior, column=15, label="Balance:")}),
             ("cleaning",
              {"dummy": ViewPageEntry(self.interior, column=16, label="Cleaning:", function=self.computeCleaning)}),
             ("agent_fee",
              {"dummy": ViewPageEntry(self.interior, column=17, label="Agent 10%:", function=self.computeAgent)}),
             ("iva",
              {"dummy": ViewPageEntry(self.interior, column=18, label="IVA (11%):", function=self.computeIVA)}),
             ("net_income",
              {"dummy": ViewPageEntry(self.interior, column=19, label="Net income:", function=self.netIncome)}),
            ]
        )
        self.forgotten_customers = []
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
        for key, widget in self.widget_view_page.items():
            widget["fields"]=[]
            
    def placeFieldsLabel(self, shift):
        column = 3
        for key, widget in self.widget_view_page.items():
            if key in self.disabled_fields:
                widget["dummy"].tk_label.pack_forget()
                widget["dummy"].reloadLabel(parent=self.disabled_fields_frame)
                widget["dummy"].tk_label.pack(side="left")
                widget["dummy"].tk_label.bind("<Button-1>", self.showField)
            elif key != "id":
                widget["dummy"].tk_label.grid_forget()
                widget["dummy"].reloadLabel()
                widget["dummy"].tk_label.grid(row=shift, column=column, sticky="NWE")                
                widget["dummy"].tk_label.bind("<Button-1>", self.hideField)
                column += 1
            else:
                widget["dummy"].tk_label.grid(row=shift, column=column, sticky="NWE")
                column += 1

        self.widget_view_page_item = odict([(item["dummy"].tk_label, item) for key, item in self.widget_view_page.items()])
        self.widget_view_page_name = odict([(item["dummy"].tk_label, key) for key, item in self.widget_view_page.items()])
        
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

    def computeCleaning(self):
        return 25.0 if self.widget_view_page["building"]["fields"][-1].tk_var.get() == "Siracusa" else 15.0

    def computeAgent(self):
        return (float(self.widget_view_page["total_price"]["fields"][-1].tk_var.get())-self.computeCleaning()-float(self.widget_view_page["agency_fee"]["fields"][-1].tk_var.get()))*0.1

    def computeIVA(self):
        return float(self.widget_view_page["total_price"]["fields"][-1].tk_var.get())*0.11
        
    def netIncome(self):
        return float(self.widget_view_page["total_price"]["fields"][-1].tk_var.get())-self.computeAgent()-self.computeCleaning()-self.computeIVA()-float(self.widget_view_page["agency_fee"]["fields"][-1].tk_var.get())

    def deleteCustomer(self, event, cid=0, cname=""):
        """
        Delete customer from the db
        """

        if tkinter.messagebox.askokcancel("Please confirm", "Are you sure to delete customer %s?"%cname, parent=self.parent):
            self.db_cursor.execute('''DELETE FROM customers WHERE id = ?''', [cid])

        self.refreshData(event)
            
        
    def removeCustomer(self, event, customer_row=0):
        """
        Remove customer from current view, resetted by "Show Data"
        """

        self.forgotten_customers.append(customer_row)
        self.refreshData(event)

    def editCustomer(self, event):
        return
        
    def showData(self, event):
        """
        Call refresh data after resetting session
        """

        self.forgotten_customers = []
        self.refreshData(event)
        
    def refreshData(self, event):
        next_row = self.data_next_row
        
        old_rows = []
        for irow in range(next_row, self.interior.grid_size()[1]):
            for srow in self.interior.grid_slaves(row=int(irow)):
                srow.grid_forget()
                srow.pack_forget()
        
        ###---fetch data
        if len(self.period_begin_var.get()) == 8:
            begin = datetime.datetime.strptime(self.period_begin_var.get(), '%d/%m/%y')
        elif len(self.period_begin_var.get()) == 10:
            begin = datetime.datetime.strptime(self.period_begin_var.get(), '%d/%m/%Y')
        if len(self.period_end_var.get()) == 8:
            end = datetime.datetime.strptime(self.period_end_var.get(), '%d/%m/%y')
        elif len(self.period_end_var.get()) == 10:
            end = datetime.datetime.strptime(self.period_end_var.get(), '%d/%m/%Y')
            
        self.db_cursor.execute('''SELECT * FROM customers WHERE arrival > ? AND departure < ? ORDER BY arrival ASC ''', [begin, end])
        customers = self.db_cursor.fetchall()
    
        ###---create rows for fetched data
        widget_list = list(self.widget_view_page.items())
        for key, widget in widget_list:
            for field in widget["fields"]:
                field.tk_widget.grid_remove()
            widget["fields"] = []
        field_sum = [0 for x in range(0, len(widget_list))]
        for row, customer in enumerate(customers):
            ###---skip removed customers
            if row in self.forgotten_customers:
                continue
            
            ###---delete button
            delete_icon = Image.open("data/img/delete_icon.png")
            delete_icon = delete_icon.resize((16, 16), Image.ANTIALIAS)
            self.delete_icon_tk = ImageTk.PhotoImage(delete_icon)
            delete_button = tkinter.ttk.Button(self.interior, image=self.delete_icon_tk)
            delete_button.image = self.delete_icon_tk
            delete_button.grid(columnspan=1, rowspan=1, column=0, row=next_row)
            delete_button.bind("<Button-1>", lambda event, cid=customer[0], cname=customer[1] :
                               self.deleteCustomer(event, cid = cid, cname = cname))
            ###---remove button
            remove_icon = Image.open("data/img/remove_icon.png")
            remove_icon = remove_icon.resize((16, 16), Image.ANTIALIAS)
            self.remove_icon_tk = ImageTk.PhotoImage(remove_icon)
            remove_button = tkinter.ttk.Button(self.interior, image=self.remove_icon_tk)
            remove_button.image = self.remove_icon_tk
            remove_button.grid(columnspan=1, rowspan=1, column=1, row=next_row)
            remove_button.bind("<Button-1>", lambda event, row=row : self.removeCustomer(event, customer_row = row))
            ###---edit button
            edit_icon = Image.open("data/img/edit_icon.png")
            edit_icon = edit_icon.resize((16, 16), Image.ANTIALIAS)
            self.edit_icon_tk = ImageTk.PhotoImage(edit_icon)
            edit_button = tkinter.ttk.Button(self.interior, image=self.edit_icon_tk)
            edit_button.image = self.edit_icon_tk
            edit_button.grid(columnspan=1, rowspan=1, column=2, row=next_row)
            edit_button.bind("<Button-1>", self.editCustomer)
            
            ###---data fields
            next_column = 3
            for index, data in enumerate(customer):
                widget = ViewPageEntry(self.interior,
                                       column=widget_list[index][1]["dummy"].column,
                                       label=widget_list[index][1]["dummy"].label)
                widget_list[index][1]["fields"].append(widget)
                if widget_list[index][0] in self.disabled_fields:
                    widget_list[index][1]["fields"][-1].tk_var.set(data)
                else:
                    widget_list[index][1]["fields"][-1].tk_widget.grid(row=next_row, column=next_column, sticky="NWE")
                    widget_list[index][1]["fields"][-1].tk_widget.config(state = "disabled")
                    widget_list[index][1]["fields"][-1].tk_var.set(data)
                    next_column += 1
                ###---compute sums if applicable
                field_sum[index] = field_sum[index]+float(data) if is_number(data) else None

            ###---compute fields that are not stored in the db
            for name, field in [(name, widgets["dummy"]) for name, widgets in self.widget_view_page.items()
                                if widgets["dummy"].function != None]:
                widget = ViewPageEntry(self.interior, column=field.column, label=field.label, function=field.function)
                widget_list[index][1]["fields"].append(widget)                
                if name in self.disabled_fields:
                    widget_list[index][1]["fields"][-1].tk_var.set(widget.function())
                else:
                    widget_list[index][1]["fields"][-1].tk_widget.grid(row=next_row, column=next_column, sticky="NWE")
                    widget_list[index][1]["fields"][-1].tk_widget.config(state = "disabled")
                    widget_list[index][1]["fields"][-1].tk_var.set(widget.function())
                    next_column += 1
                ###---compute sums if applicable
                field_sum[widget.column] += widget.function()
                
            next_row += 1

        ###---display sums
        if len(customers) > 0:
            self.sum_line = tkinter.ttk.Separator(self.interior, orient="horizontal")
            self.sum_line.grid(row=next_row, columnspan=len(widget_list), sticky="EW")
            next_row += 1
            next_column = 3
            for index, field in enumerate(widget_list):
                if field[0] in self.disabled_fields:
                    continue
                widget = ViewPageEntry(self.interior, column=field[1]["dummy"].column, label=field[1]["dummy"].label)
                widget_list[index][1]["fields"].append(widget)
                widget_list[index][1]["fields"][-1].tk_widget.grid(row=next_row, column=next_column, sticky="NWE")
                widget_list[index][1]["fields"][-1].tk_widget.config(state = "disabled")
                value = field_sum[index] if field_sum[index] else ""
                value = "Total:" if widget.column == 0 else value
                widget_list[index][1]["fields"][-1].tk_var.set(value)
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
        
