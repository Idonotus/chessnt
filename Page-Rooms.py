import tkinter as tk
from tkinter import _Cursor, _Relief, _ScreenUnits, _TakeFocusValue, Menu, Misc, ttk
from typing import Any
from typing_extensions import Literal

class CreationPopUp(tk.Toplevel):
    def __init__(self, master) -> None:
        self.master=master
        super().__init__(master)
        self.name=ttk.Entry(self)
        self.name.grid(row=1)
        ttk.Label(self,text="Room name").grid(row=0)
        self.password=ttk.Entry(self)
        self.password.grid(row=2)
        ttk.Label(self,text="Room password").grid(row=3)

class RoomPage(ttk.Frame):
    def __init__(self,master=None,main=None) -> None:
        self.main=main
        if self.main:
            self.s=main.s
        else:
            self.s=None
        if not master:
            master=tk.Tk()
        super().__init__(master)
        self.pack(fill="both",expand=True)
        roomselcon=tk.Frame(self,bg="red")
        roomselcon.grid(row=0,column=0,sticky="NEWS")
        chatcon=tk.Frame(self,bg="green",width=10,height=10)
        chatcon.grid(row=0,column=1,sticky="NEWS")
        self.grid_columnconfigure(1,weight=6)
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(0,weight=1)
        self.roomlist=tk.Listbox(roomselcon)
        self.roomlist.grid(row=0,column=0,columnspan=3,sticky="NEWS")
        roomselcon.grid_columnconfigure(0,weight=1)
        roomselcon.grid_columnconfigure(1,weight=1)
        roomselcon.grid_columnconfigure(2,weight=1)
        roomselcon.grid_rowconfigure(0,weight=1)
        ttk.Button(roomselcon,text="Join room").grid(row=1,column=0,sticky="WE")
        ttk.Button(roomselcon,text="Join directly").grid(row=1,column=1,sticky="WE")
        ttk.Button(roomselcon,command=lambda:self.popup(CreationPopUp),text="Create room").grid(row=1,column=2,sticky="WE")

    def popup(self,popupmenu):
        popupmenu(self)
if __name__=="__main__":
    r=RoomPage()
    tk.mainloop()