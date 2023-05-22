import tkinter as tk
from tkinter import ttk
from WigExtras import UserData,UserList
from Chess.GameGraphics import Gui

class ChessPage(ttk.Frame):
    name="Pchess"
    def __init__(self,master=None,main=None) -> None:
        self.main=main
        if main:
            self.s=main.s
        else:
            self.s=None

        super().__init__(master=master,height=700,width=1300)
        
        self.grid_propagate(0)
        self.grid_columnconfigure(1,weight=1)
        self.grid_columnconfigure(0,weight=2)
        self.grid_rowconfigure(0,weight=1)

        self.g=Gui(self,signal=None,tile=85)
        self.g.grid(column=0,row=0)
        nb=ttk.Notebook(self)
        nb.grid(column=1,row=0,sticky="NEWS")
        self.ulist=UserList(nb)
        self.ulist.pack()
        nb.add(self.ulist,text="Users")

    def adduser(self,name,auth=False):
        a=UserData(self.ulist.getmaster(),name,auth=auth)
        self.ulist.insert(a)
if __name__=="__main__":
    v=ChessPage()
    v.pack(expand=True,fill="both")
    v.adduser("pizza")
    v.adduser("testing",auth=True)
    v.adduser("AAAAAAAAAAAAAAA",auth=False)
    v.adduser("L bozo||>|><XS@CSKAEJHAUIOGOUHI",auth=True)
    v.mainloop()