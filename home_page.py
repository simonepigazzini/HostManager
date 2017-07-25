#!/bin/python3

import os
import tkinter
import time
import subprocess

from PIL import Image, ImageTk
from tkinter import messagebox
from tkinter.ttk import *

class HomePageWidget():
    def __init__(self, parent, column=0, row=0, label="", figure=""):
        self.parent = parent
        self.column = int(column)
        self.row = int(row)
        self.label = label
        self.figure = figure

        icon = Image.open(self.figure)
        icon = icon.resize((128, 128), Image.ANTIALIAS)
        self.icon_tk = ImageTk.PhotoImage(icon)
        self.button = tkinter.ttk.Button(self.parent, image=self.icon_tk)
        self.button.image = self.icon_tk

        self.tk_label_str = tkinter.StringVar()
        self.tk_label = tkinter.ttk.Label(self.parent, textvariable=self.tk_label_str, style="HM.TLabel")

class HomePage():
    def __init__(self, parent=None):
        ###---create from parent class
        self.parent = parent
        #self.parent.bind("<Configure>", self.autoResize)

        ###---set style
        tkinter.ttk.Style().configure("HM.TLabel", anchor="w", foreground="black")

        ###---global static page widget
        ###---analyzed period begin
        #main_frame = tkinter.ttk.Frame(self.parent)

        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_columnconfigure(1, weight=1)
        self.parent.grid_columnconfigure(2, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_rowconfigure(3, weight=1)

        ###---Update button (code only)
        self.update_w = HomePageWidget(self.parent, column=0, row=1, label="UPDATE", figure="data/img/update_icon.png")
        self.update_w.button.grid(columnspan=1, rowspan=1, column=self.update_w.column, row=self.update_w.row)
        self.update_w.button.bind("<Button-1>", lambda event : self.updateCallback)
        self.update_w.tk_label.grid(row=self.update_w.row+1, column=self.update_w.column, sticky="")
        self.update_w.tk_label_str.set(self.update_w.label)

        ###---Download button (code only)
        self.download_w = HomePageWidget(self.parent, column=1, row=1, label="DOWNLOAD", figure="data/img/download_icon.png")
        self.download_w.button.grid(columnspan=1, rowspan=1, column=self.download_w.column, row=self.download_w.row)
        self.download_w.button.bind("<Button-1>", lambda event : self.downloadCallback)
        self.download_w.tk_label.grid(row=self.download_w.row+1, column=self.download_w.column, sticky="")
        self.download_w.tk_label_str.set(self.download_w.label)

        ###---Upload button (code only)
        self.upload_w = HomePageWidget(self.parent, column=2, row=1, label="UPLOAD", figure="data/img/upload_icon.png")
        self.upload_w.button.grid(columnspan=1, rowspan=1, column=self.upload_w.column, row=self.upload_w.row)
        self.upload_w.button.bind("<Button-1>", lambda event : self.uploadCallback)
        self.upload_w.tk_label.grid(row=self.upload_w.row+1, column=self.upload_w.column, sticky="")
        self.upload_w.tk_label_str.set(self.upload_w.label)

    def updateCallback(self):
        """
        Download db changes only:
        1) git fetch origin
        2) git merge --no-commit --no-ff origin/master
        3) git reset -- data/db/customer.db
        4) git commit
        """

        subprocess.getoutput('git fetch origin')
        subprocess.getoutput('git merge --no-commit --no-ff origin/master')
        subprocess.getoutput('git reset -- data/db/customer.db')
        subprocess.getoutput('git commit')

    def downloadCallback(self):
        """
        Download db changes only:
        1) git fetch origin
        2) git checkout --patch origin/master data/db/customer.db
        """

        subprocess.getoutput('git fetch origin')
        subprocess.getoutput('git checkout --patch origin/master data/db/customer.db')
    
    def uploadCallback(self):
        """
        Update database only:
        1) git add data/db/customer.db
        2) git commit -m "Uploading db to repo"
        3) git push origin master
        """

        print("hola")
        subprocess.getoutput('git add data/db/customer.db')
        subprocess.getoutput('git commit -m "Uploading db to repo"')
        subprocess.getoutput('git push origin master')
