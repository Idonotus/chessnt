import tkinter as tk
from tkinter import ttk
class chatWidget(ttk.Frame):
    def __init__(self,master,sendcom=None) -> None:
        super().__init__(master)
        self.grid_rowconfigure(0,weight=1)
        self.grid_columnconfigure(0,weight=1)
        self.chathistory=tk.Listbox(self)
        self.chathistory.grid(row=0,column=0,columnspan=2)
        self.chatentry=ttk.Entry(self)
        self.chatentry.grid(row=1,column=0)
        chatExec=ttk.Button(self,text="Send")
        chatExec.grid(row=1,column=1)
    
    def chatupdate(self,hist:list) -> None:
        self.chathistory.delete(0,tk.END)
        for item in hist:
            self.chathistory.insert(tk.END,item)
    