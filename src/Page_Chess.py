import tkinter as tk
from tkinter import ttk
from WigExtras import UserData,UserList
from Chess.Graphics import Gui
import random
from Chess.vectormath import vector

def button(master,name,command):
    return lambda: ttk.Button(master=master,text=name,command=command)
class ChessPage(ttk.Frame):
    name="Pr-chess"
    def __init__(self,master=None,main=None) -> None:
        self.main=main
        if main:
            self.s=main.s
            self.s.send({"mod":"rooms","forwardtoroom":True,"com":"getusers"})
            self.s.send({"mod":"rooms","forwardtoroom":True,"com":"getboard"})
            self.s.send({"com":"getauth","action":"gametoggle","mod":"rooms","forwardtoroom":True,})
        else:
            self.s=None

        super().__init__(master=master,height=700,width=1300)
        self.pack(fill="both",expand=True)
        self.grid_propagate(0)
        self.grid_columnconfigure(1,weight=1)
        self.grid_columnconfigure(0,weight=2)
        self.grid_rowconfigure(0,weight=1)
        self.g=Gui(self,signal=None,tile=85)
        self.g.grid(column=0,row=0,rowspan=2)
        nb=ttk.Notebook(self)
        nb.grid(column=1,row=0,sticky="NEWS")
        self.ulist=UserList(nb)
        self.ulist.pack()
        nb.add(self.ulist,text="Users")
        bf=ttk.Frame(self)
        bf.grid(row=1,column=1,sticky="WE")
        bf.grid_columnconfigure(1,weight=1)
        bf.grid_columnconfigure(0,weight=1)
        self.startbutton=button(bf,"Start",self.togglegame)
        self.stopbutton=button(bf,"Stop",self.togglegame)
        ttk.Button(bf,text="Exit",command=self.leave).grid(column=1,row=0,sticky="WE")
        self.game_toggle=self.startbutton()
        self.togauth=False
        self.running=False
        self.g.automaticreturn=False
        self.teamauth={}

    def leave(self):
        if self.s:
            c={"com":"leaveroom","mod":"rooms"}
            self.s.send(c)

    def togglegame(self):
        c={"com":"togglegamerun","forwardtoroom":True,"mod":"rooms"}
        self.s.send(c)

    def adduser(self,name,auth=False,team=None):
        a=UserData(self.ulist.getmaster(),name,auth=auth,team=team,command=self.teamSetEvent)
        a.setTeam("None")
        self.ulist.insert(a)
    
    def teamSetEvent(self,team,d:UserData):
        if self.s:
            c={"mod":"rooms","forwardtoroom":True,"com":"setteam","user":d.getUsername(),"team":team}
            self.s.send(c)
            return
        self.ulist.setTeam(d.getUsername(),team)
    


    def guisig(self,*data):
        if not self.s:
            return
        match data:
            case ("pickup_piece",int(x),int(y)):
                c={"mod":"rooms","forwardtoroom":True,"com":"getmoves","piecepos":(x,y)}
                self.s.send(c)
            case ("drop_piece",vector(a,b),vector(c,d)):
                c={"mod":"rooms","forwardtoroom":True,
                   "com":"makemove","pos1":(int(a),int(b)),"pos2":(int(c),int(d))}
                self.s.send(c)

    def updatetoggle(self):
        self.game_toggle.grid_forget()
        if self.togauth:
            self.game_toggle.grid(column=0,row=0,sticky="WE")
    
    def changeteamauth(self):
        if self.running:
            for u in self.ulist.users.keys():
                self.ulist.setAuth(u,False)
        else:
            for i in self.teamauth.items():
                self.ulist.setAuth(*i)

    def handleCommand(self,com):
        match com:
            case {"com":"displaymoves","moves":allavail,**_u}:
                self.g.removehighlight("move")
                if not self.g.draggable:
                    return
                allavail=[vector(p[0],p[1]) for p in allavail]
                self.g.highlighttiles(allavail,highlight="move")
            case {"com":"teamchanged","name":name,"team":team,**_u}:
                self.ulist.setTeam(name,team)
            case {"com":"userjoin","user":name,"auth":auth,**_u}:
                self.adduser(name,auth)
            case {"com":"userleave","user":name,**_u}:
                self.ulist.removeName(name)
            case {"com":"loadmoves","dif":dif,**_u}:
                self.g.applychanges(dif)
            case {"com":"setauth","user":dict(users),"action":"setteam",**_u}:
                self.teamauth.update(users)
                self.changeteamauth()
            case {"com":"setauth","action":"gametoggle","auth":sauth}:
                self.togauth=sauth
                self.updatetoggle()
            case {"com":"loadboard","data":d,**_u}:
                self.g.destroy()
                self.g=Gui.genboard(master=self,dim=d["dim"],boarddata=d["boarddata"],signal=self.guisig)
                self.g.automaticreturn=False
                self.g.grid(column=0,row=0,rowspan=2)
                if "running" not in d:
                    return
                self.game_toggle.destroy()
                self.running=d["running"]
                if d["running"]:
                    self.game_toggle=self.stopbutton()
                else:
                    self.game_toggle=self.startbutton()
                    self.g.highlightalltiles("default")
                self.updatetoggle()
                self.changeteamauth()                

            case {"com":"loaduser","data":data}:
                for n in self.ulist.users:
                    self.ulist.removeName(n)
                for item in data:
                    self.adduser(*item)

            case {"com":"highlightboard","highlight":highlight,**_u}:
                self.g.highlightboard(highlight=highlight)
            case {"com":"returnpiece","pos":[x,y],**_u}:
                p=self.g.getpiece(x,y)
                self.g.placepiece(p,x,y)
if __name__=="__main__":
    v=ChessPage()
    v.pack(expand=True,fill="both")
    v.adduser("pizza")
    v.adduser("testing",auth=True)
    v.adduser("AAAAAAAAAAAAAAA",auth=False)
    v.adduser("L bozo||>|><XS@CSKAEJHAUIOGOUHI",auth=True)
    for n in v.ulist.users:
        v.ulist.setTeam(n,random.choice(v.ulist.users[n].possibleteams))
    v.ulist.removeName("L bozo||>|><XS@CSKAEJHAUIOGOUHI")
    v.mainloop()