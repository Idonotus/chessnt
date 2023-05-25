from Page_Login import LoginPage
from Page_Con import ConnectPage
from Page_Rooms import RoomPage
from NetHandler import appNetClient
import tkinter as tk
from tkinter import ttk
import logging
import threading
logging.basicConfig(format="[%(levelname)s] %(message)s",level=logging.DEBUG)
#453C67
#191825
#6D67E4
#865DFF
#E384FF
#FFA3FD
pagelookup={
    ConnectPage.name:ConnectPage,
    LoginPage.name:LoginPage,
    RoomPage.name:RoomPage
}

class mainApp:
    def __init__(self):
        self.win=tk.Tk()
        self.win.geometry("1300x700")
        self.style=ttk.Style(self.win)
        self.style.layout("TEntry")
        self.style.theme_use("alt")
        self.style.configure(".",background="#191825",foreground="#865DFF")
        self.style.map("TButton",background=[
                                    ("pressed","#46C2CB"),
                                    ("disabled","#6D5D6E"),
                                    ("active","#453C67"),
                                    ("!active","#393646")],
                                relief=[("pressed","sunken"),
                                    ("!pressed","flat")])
        self.style.map("TEntry",fieldbackground=[
                                    ("focus","#E384FF"),
                                    ("active","#865DFF"),
                                    ("!active","#6D67E4")
                                ])

        self.style.configure("TButton",focuscolor="#46C2CB")
        self.style.configure("Error.TLabel",foreground="#46C2CB")
        self.backproc={}
        self.curpage=None
        self.s=appNetClient(self)
        self.pagelock=threading.Lock()
        self.page(ConnectPage.name)
        
    def page(self,page):
        with self.pagelock:
            if self.curpage:
                self.curpage.destroy()
            if page not in pagelookup:
                raise FileNotFoundError(f"Requested page: {page} not in dict")
            self.curpage=pagelookup[page](self.win,self)

    def handleCommand(self,command):
        if "mod" not in command:
            return
        if command["mod"] in self.backproc:
            self.backproc[command["mod"]].handleCommand(command)
        elif command["mod"] == self.curpage.name:
            self.curpage.handleCommand(command)
    def createBackProc(self,name,obj):
        self.backproc[name]=obj

if __name__=="__main__":
    mainApp()
    logging.info("Starting app")
    tk.mainloop()
