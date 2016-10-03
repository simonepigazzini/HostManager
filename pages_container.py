#!/bin/python3

import os
import tkinter

from tkinter.ttk import *
from collections import OrderedDict as odict

class PagesContainerApp(tkinter.Tk):
    def __init__(self, parent=None):
        ###---create from parent class
        tkinter.Tk.__init__(self, parent)

        ###---class objects
        self.n_tabs = 0
        self.current_tab = 0
        self.pages = odict()
        self.notebook = tkinter.ttk.Notebook(self)


    def new_page(self, name):
        """
        Create new page and insert tab for it in the notebook, returns the newly created page
        """

        self.n_tabs += 1
        self.pages[name] = tkinter.ttk.Frame(self.notebook)
        self.notebook.add(self.pages[name], text=name)
        self.notebook.bind("<Tab>", self.next_tab)
        self.notebook.pack(expand=1, fill="both")

        return self.pages[name]

    def next_tab(self, event):
        """
        Cycle through tabs with <Tab>
        """

        self.current_tab = self.current_tab+1 if self.current_tab < self.n_tabs else 0        
        self.notebook.select(self.current_tab)
