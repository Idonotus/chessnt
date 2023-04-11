from Page_Login import LoginPage
from Page_Con import ConnectPage
from NetHandler import appNetClient
import tkinter as tk
from tkinter import ttk
import logging
logging.basicConfig(format="[%(levelname)s] %(message)s",level=logging.DEBUG)


pagelookup={
    ConnectPage.name:ConnectPage,
    LoginPage.name:LoginPage
}

class mainApp:
    def __init__(self):
        self.win=tk.Tk()
        self.backproc={}
        self.curpage=ConnectPage(self.win,self)
        self.s=appNetClient(self)
        
    def page(self,page):
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