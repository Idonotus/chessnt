import tkinter as tk
from tkinter import ttk
ERRORS={
    "NameLenErr": "Room name has to be between 3 and 20 characters",
    "PrivTypeErr" : "PrivTypeErr: Please contact dev",
    "PassLenErr" : "Password must be less than 30 characters"
}
SUCCESS={
    "CredSuccess",
    "CreationSuccess",
    "JoinSuccess"
}

class DJPopUp(tk.Toplevel):
    def __init__(self,master):
        self.master=master
        super().__init__(master)
        self.grid_columnconfigure(0,weight=1)
        ttk.Label(self,text="Room name").grid(row=0)
        self.name=ttk.Entry(self)
        self.name.grid(row=1)
        ttk.Label(self,text="Room password").grid(row=2)
        self.password=ttk.Entry(self)
        self.password.grid(row=3)
        ttk.Button(self,text="Join Room")

class CreationPopUp(tk.Toplevel):
    def __init__(self, master) -> None:
        self.master=master
        super().__init__(master)
        self.grid_columnconfigure(0,weight=1)
        ttk.Label(self,text="Room name").grid(row=0)
        self.name=ttk.Entry(self)
        self.name.grid(row=1)
        ttk.Label(self,text="Room password").grid(row=2)
        self.password=ttk.Entry(self)
        self.password.grid(row=3)
        cf=ttk.Frame(self)
        cf.grid(row=4)
        self.error=ttk.Label(self)
        self.error.grid(row=6)
        self.private=tk.BooleanVar(self)
        ttk.Checkbutton(cf,variable=self.private).grid(column=0,row=0)
        ttk.Label(cf,text="Private").grid(column=1,row=0)
        ttk.Button(self,text="Create",command=self.collectEntries).grid(row=5)
    
    def collectEntries(self):
        priv=self.private.get()
        roomname=self.name.get()
        roompass=self.password.get()
        r=roomcredcheck(roomname,roompass,priv)
        if r[0]:
            self.master.createroom(roomname,roompass,priv)
        else:
            if r[1] in ERRORS:
                self.error.config(text=ERRORS[r[1]])
            else:
                self.error.config(text="Unknown Error: Please try again")

class RoomPage(ttk.Frame):
    name="Proomsel"
    def __init__(self,master=None,main=None) -> None:
        self.main=main
        self.curpopup:tk.Toplevel=None
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
        self.grid_columnconfigure(1,weight=10)
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(0,weight=1)
        self.roomlist=tk.Listbox(roomselcon)
        self.roomlist.grid(row=0,column=0,columnspan=3,sticky="NEWS")
        roomselcon.grid_columnconfigure(0,weight=1)
        roomselcon.grid_columnconfigure(1,weight=1)
        roomselcon.grid_columnconfigure(2,weight=1)
        roomselcon.grid_rowconfigure(0,weight=1)
        ttk.Button(roomselcon,text="Join room").grid(padx=5,row=1,column=0,sticky="WE")
        ttk.Button(roomselcon,text="Join directly").grid(row=1,column=1,sticky="WE")
        ttk.Button(roomselcon,command=lambda:self.popup(CreationPopUp),text="Create room").grid(pady=10,padx=5,row=1,column=2,sticky="WE")

    def popup(self,popupmenu,**kwargs):
        if self.curpopup:
            self.curpopup.destroy()
        self.curpopup=popupmenu(self,**kwargs)

    def createroom(self,roomname,roompass="",private=False):
        com={
            "com":"createroom",
            "mod":"rooms",
            "roomname":roomname,
            "roompass":roompass,
            "private":private
            }
        if self.s:
            self.s.send(com)

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
    tk.mainloop()