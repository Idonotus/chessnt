from Page_Login import LoginPage
from Page_Con import ConnectPage
from NetHandler import netClient

class appNetClient(netClient):
    def __init__(self,main=None) -> None:
        self.main=main
        super().__init__()
    def disconnect(self):
        if self.main:
            self.main.page("connect")
        return super().disconnect()

pagelookup={
    "main":None,
    ConnectPage.name:ConnectPage,
    LoginPage.name:LoginPage
}

class mainApp:
    def __init__(self):
        self.backproc={}
        self.curpage=None
        self.s=appNetClient(self)
        
    def page(self,page):
        if page not in pagelookup:
            raise FileNotFoundError(f"Requested page: {page} not in dict")

    def handlecommand(self,command):
        if command["mod"] in self.backproc:
            self.backproc.handleCommand(command)
        elif command["mod"] == self.curpage.name:
            self.curpage.handleCommand(command)
    def createBackProc(self,name,obj):
        self.backproc[name]=obj
