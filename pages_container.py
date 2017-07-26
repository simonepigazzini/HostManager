#!/bin/python3

import os
import tkinter

from tkinter.ttk import *
from collections import OrderedDict as odict

class PagesContainerApp(tkinter.ttk.Frame):
    def __init__(self, parent=None):
        ###---create from parent class
        tkinter.ttk.Frame.__init__(self, parent)
        self.grid()
        
        ###---class objects
        self.n_tabs = 0
        self.current_tab = 0
        self.pages = odict()
        self.notebook = tkinter.ttk.Notebook(self)
        self.notebook.enable_traversal()
        
        ###---set notebook style: 'aqua' if available (i.e. on MAC) 'alt' otherwise
        if "aqua" in tkinter.ttk.Style().theme_names():            
            tkinter.ttk.Style().theme_use("aqua")
        else:
            tkinter.ttk.Style().theme_use("alt")
        tkinter.ttk.Style().configure(".", font='TkDefaultFont 11')
        
    def addTab(self, name):
        """
        Create new page and insert tab for it in the notebook, returns the newly created page
        """

        self.n_tabs += 1
        self.pages[name] = tkinter.ttk.Frame(self)
        self.notebook.add(self.pages[name], text=name, underline=0)
        self.notebook.pack(expand=1, fill="both")
        # tkinter.ttk.Style().configure("HM.TFrame", background="black")
        # self.pages[name].config(style="HM.TFrame")

        return self.pages[name]
