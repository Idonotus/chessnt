import tkinter as tk
from tkinter import ttk,messagebox
from WigExtras import NameEntry,LenPassEntry,chatWidget
import json
import logging
ERRORS={
    "NameLenErr": "Room name has to be between 3 and 20 characters",
    "PrivTypeErr" : "PrivTypeErr: Please contact dev",
    "PassLenErr" : "Password must be less than 30 characters",
    "RoomExists" : "The room you are trying to create exists",
    "AuthDeny" : "There was an error when connecting to room"
}
SUCCESS={
    "CredSuccess",
    "CreationSuccess",
    "JoinSuccess"
}

class GetPassPopUp(tk.Frame):
    def __init__(self,master,page,roomname):
        super().__init__(master)
        self.roomname=roomname
        self.awaiting=False
        self.page=page
        r=ttk.Frame(self)
        r.pack(expand=True,fill="both")
        ttk.Label(r,text="Password required").grid(row=0,column=0)
        self.password=LenPassEntry(r,1,100)
        self.password.grid(row=1,column=0)
        self.grid_columnconfigure(0,weight=1)
        self.b=ttk.Button(r,text="Confirm",command=self.collectEntries)
        self.b.grid(row=2)
        self.pack()

    def collectEntries(self):
        if self.password.isvalid():
            password=self.password.get()
            self.page.reqjoinroom(self.roomname,password)
            self.master.destroy()

class DJPopUp(tk.Frame):
    def __init__(self,master,page):
        self.master=master
        self.page=page
        super().__init__(master)
        self.grid_columnconfigure(0,weight=1)
        ttk.Label(self,text="Room name").grid(row=0)
        self.name=NameEntry(self)
        self.name.grid(row=1)
        ttk.Label(self,text="Room password").grid(row=2)
        self.password=LenPassEntry(self,0,100)
        self.password.grid(row=3)
        self.b=ttk.Button(self,text="Join Room",command=self.collectEntries)
        self.b.grid(row=4)
        self.pack()    
    def collectEntries(self):
        if self.name.isvalid() and self.password.isvalid():
            roomname=self.name.get()
            roompass=self.password.get()
            self.page.reqjoinroom(roomname,roompass)
            self.master.destroy()
class CreationPopUp(ttk.Frame):
    def __init__(self, master, page) -> None:
        self.master=master
        self.page=page
        super().__init__(master)
        self.grid_columnconfigure(0,weight=1)
        ttk.Label(self,text="Room name").grid(row=0)
        self.name=NameEntry(self)
        self.name.grid(row=1)
        ttk.Label(self,text="Room password").grid(row=2)
        self.password=LenPassEntry(self,0,100)
        self.password.grid(row=3)
        cf=ttk.Frame(self)
        cf.grid(row=4)
        self.error=ttk.Label(self)
        self.error.grid(row=6)
        self.private=tk.BooleanVar(self)
        ttk.Checkbutton(cf,variable=self.private).grid(column=0,row=0)
        ttk.Label(cf,text="Private").grid(column=1,row=0)
        self.b=ttk.Button(self,text="Create",command=self.collectEntries)
        self.b.grid(row=5)
        self.pack()
    
    def collectEntries(self):
        if self.name.isvalid() and self.password.isvalid():
            priv=self.private.get()
            roomname=self.name.get()
            roompass=self.password.get()
            self.page.reqcreateroom(roomname,roompass,priv)
            self.master.destroy()


class RoomPage(ttk.Frame):
    name="Pr-sel"
    def __init__(self,master=None,main=None) -> None:
        self.main=main
        self.curpopup:tk.Toplevel=None
        if self.main:
            self.s=main.s
            self.s.send({
            "com":"getrooms",
            "mod":"rooms"
        })
        else:
            self.s=None
        if not master:
            master=tk.Tk()
            master.geometry("1300x700")
        super().__init__(master)
        self.pack(fill="both",expand=True)
        roomselcon=ttk.Frame(self)
        roomselcon.grid(row=0,column=0,sticky="NEWS")
        chatcon=chatWidget(self)
        chatcon.grid(row=0,column=1,sticky="NEWS")
        self.grid_columnconfigure(1,weight=10)
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(0,weight=1)
        self.roomlist=tk.Listbox(roomselcon,selectmode=tk.SINGLE)
        self.roomlist.grid(row=0,column=0,columnspan=4,sticky="NEWS")
        self.roomdata={}
        self.rooms=[]
        roomselcon.grid_columnconfigure(0,weight=1)
        roomselcon.grid_columnconfigure(1,weight=1)
        roomselcon.grid_columnconfigure(2,weight=1)
        roomselcon.grid_rowconfigure(0,weight=1)
        ttk.Button(roomselcon,text="Create room",command=lambda: self.popup(CreationPopUp)).grid(padx=2,row=1,column=0,sticky="WE")
        ttk.Button(roomselcon,text="Join room",command=self.joinselected).grid(padx=2,row=1,column=1,sticky="WE")
        ttk.Button(roomselcon,command=lambda:self.popup(DJPopUp),text="Join directly").grid(row=1,column=2,sticky="WE",padx=2)
        ttk.Button(roomselcon,text="Refresh",command=self.refresh).grid(padx=2,row=1,column=3,sticky="WE")
        
        

    def refresh(self):
        com={
            "com":"getrooms",
            "mod":"rooms"
        }
        if self.s:
            self.s.send(com)

    def joinselected(self):
        s=self.roomlist.curselection()
        if len(s)==0:
            return
        n=self.roomlist.get(s[0])
        if n in self.rooms:
            d=self.roomdata[n]
            if d["password"]:
                self.popup(GetPassPopUp,roomname=n)
            else:
                self.reqjoinroom(n,"")
        else:
            logging.error("Room list desync")
            self.loadRoomlist(self.rooms)

    def popup(self,popupmenu,**kwargs):
        if self.curpopup:
            self.curpopup.destroy()
        self.curpopup=tk.Toplevel(self)
        popupmenu(self.curpopup,self,**kwargs)
        
        

    def reqjoinroom(self,roomname,roompass=""):
        com={
            "com":"joinroom",
            "mod":"rooms",
            "roomname":roomname,
            "roompass":roompass
        }
        if self.s:
            self.s.send(com)

    def reqcreateroom(self,roomname,roompass="",private=False):
        com={
            "com":"createroom",
            "mod":"rooms",
            "roomname":roomname,
            "roompass":roompass,
            "private":private
            }
        if self.s:
            self.s.send(com)
    
    def loadRoomlist(self,roomlist):
        self.roomlist.delete(0,tk.END)
        self.rooms=[]
        self.roomdata={}
        for item in roomlist:
            self.addRoom(item)
    
    def addRoom(self,roomdata):
        print(roomdata)
        if "private" in roomdata:
            if roomdata["private"]:
                return
        self.roomlist.insert(tk.END,roomdata["name"])
        self.roomdata[roomdata["name"]]=roomdata
        self.rooms.append(roomdata["name"])
        if roomdata["password"]:
            self.roomlist.itemconfig(tk.END,bg="#F97B22",selectbackground="#FC4F00")
    
    def removeRoom(self,name):
        try:
            i=self.rooms.index(name)
        except:
            return
        self.rooms.pop(i)
        self.roomdata.pop(name)
        self.roomlist.delete(i)

    def handleCommand(self,com):
        match com:
            case {"com":"refreshrooms","roomarray":rooms,**_u}:
                self.loadRoomlist(rooms)
            case {"com":"showroom","name":name,"password":ispassprot,**_u}:
                ispriv=False
                if "private" in _u:
                    ispriv=_u["private"]
                self.addRoom({"name":name,"password":ispassprot,"private":ispriv})
            case {"com":"hideroom","name":name}:
                self.removeRoom(name)
            case {"com":"raiseError","type":"AuthDeny"}:
                messagebox.showerror("Could not join room ¯\_(ツ)_/¯")
            case {"com":"raiseError","type":"RoomExists"}:
                messagebox.showerror("This room already exists")
            

def roomcredcheck(roomname,roompass="",private=False):
    if not 3<=len(roomname)<=20:
        return (False,"NameLenErr")
    if not(private is False or private is True):
        return (False,"PrivTypeErr")
    if len(roompass)>30:
        return (False,"PassLenErr")
    return (True,"credsuccess")

if __name__=="__main__":
    r=RoomPage()
    with open("testrooms.json","r") as f:
        c=f.read()
    r.loadRoomlist(json.loads(c))
    tk.mainloop()