from typing import Any
from Page_Login import LoginPage
from Page_Con import ConnectPage
from Page_Rooms import RoomPage
from NetHandler import appNetClient
from Page_Chess import ChessPage
import tkinter as tk
from tkinter import ttk,messagebox
import logging
import threading

logging.basicConfig(format="[%(asctime)s][%(levelname)s] %(name)s: %(message)s",datefmt="%d-%m-%Y %H:%M:%S",level=logging.DEBUG)
COLORS={
    "baseback":"#1B2431",
    "text":"#bba4ff",
    "widgetback":"#343837",
    "backhover":"#453C67",
    "press":"#46C2CB",
    "disable":"#6D5D6E",
    "accent":"#46C2CB",
    "fieldaccent":"#004802"
}
pagelookup={
    ConnectPage.name:ConnectPage,
    LoginPage.name:LoginPage,
    RoomPage.name:RoomPage,
    ChessPage.name:ChessPage
}

class stateHandler:
    def __init__(self,main) -> None:
        self.main=main
        self.name=None

    def login(self,name):
        self.main.page(RoomPage.name)
        self.name=name
    
    def disconnect(self):
        self.main.page(ConnectPage.name)
        self.name=None

    def logout(self):
        self.main.page(LoginPage.name)
        self.name=None
    
    def connect(self):
        self.main.page(LoginPage.name)
    
    def loadroom(self,roomname):
        try:
            self.main.page(roomname)
        except FileNotFoundError:
            logging.error(f"{roomname} not a valid page")
            raise

    def handleCommand(self,com):
        match com:
            case {"com":"login","user":name,**_u}:
                self.login(name)
            case {"com":"logout",**_u}:
                self.logout()
            case {"com":"joinroom","type":roomtype,**_u}:
                try:
                    self.loadroom(roomtype)
                except:
                    com={"com":"leaveroom","mod":"rooms"}
                    logging.exception()
            case {"com":"leftroom",**_u}:
                self.main.page(RoomPage.name)
            case {"com":"raiseError","type":"NotInRoom"}:
                messagebox.showerror("This should not happen","You have become desynced. Please contact dev")

class mainApp:
    def __init__(self):
        self.win=tk.Tk()
        self.win.title("Chessn't")
        self.win.geometry("1300x700")
        self.win.protocol("WM_DELETE_WINDOW",self.onclose)

        self.style=ttk.Style(self.win)
        self.style.layout("TEntry")
        self.style.theme_use("alt")
        self.style.configure(".",background=COLORS["baseback"],foreground="#865DFF")
        self.style.map("TButton",background=[
                                    ("pressed",COLORS["press"]),
                                    ("disabled",COLORS["disable"]),
                                    ("active",COLORS["backhover"]),
                                    ("!active",COLORS["widgetback"])],
                                relief=[("pressed","sunken"),
                                    ("!pressed","flat")])
        self.style.map("TEntry",fieldbackground=[
                                    ("focus",COLORS["fieldaccent"]),
                                    ("!active",COLORS["widgetback"])],
                                )
        self.style.configure("TEntry",foreground=COLORS["text"])
        self.style.configure("TButton",focuscolor=COLORS["accent"])
        self.style.configure("Error.TLabel",foreground=COLORS["accent"])


        self.backproc={}
        self.curpage:Any=None
        self.s=appNetClient(self)
        self.pagelock=threading.Lock()
        self.page(ConnectPage.name)
        self.stateHandler=stateHandler(self)
        self.loadBackProc("stateHandler",self.stateHandler)

    def onclose(self):
        self.s.close()
        self.win.destroy()

    def page(self,page):
        with self.pagelock:
            if self.curpage:
                self.curpage.destroy()
            if page not in pagelookup:
                raise FileNotFoundError(f"Requested page: {page} not in dict")
            self.curpage=pagelookup[page](self.win,self)

    def handleCommand(self,command):
        if "mod" not in command or "com" not in command:
            return
        if command["com"]=="raiseError":
            logging.error(f"Server exception recieved:\n{command}")
        if command["mod"] in self.backproc:
            self.backproc[command["mod"]].handleCommand(command)
        elif command["mod"] == self.curpage.name:
            self.curpage.handleCommand(command)
    def loadBackProc(self,name,obj):
        self.backproc[name]=obj

if __name__=="__main__":
    mainApp()
    logging.info("Starting app")
    tk.mainloop()
