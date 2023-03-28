import tkinter as tk
from tkinter import ttk
import socket
class loginmenu(ttk.Frame):
    def __init__(self,Toolru) -> None:
        self.Toolru=Toolru
        self.notebook=Toolru.notebook
        super().__init__(master=self.notebook,height=700,width=1000)
        self.pack(fill="both",expand=True)
        inputmenu=ttk.Frame(self,width=400,height=200)
        inputmenu.pack(pady=200,padx=300)
        self.ip = ttk.Entry(inputmenu,width=20)
        self.iport =ttk.Entry(width=5,master=inputmenu)
        self.iuser = ttk.Entry(width=30,master=inputmenu)
        ttk.Label(inputmenu,text="IP").grid(sticky="W",row=2)
        self.ip.grid(sticky="W",row=3,padx=10,pady=5)
        ttk.Label(inputmenu,text="Port").grid(sticky="W",row=4)
        self.iport.grid(sticky="W",pady=5,padx=10,row=5)
        ttk.Label(inputmenu,text="Username").grid(sticky="W",row=0)
        self.iuser.grid(sticky="W",pady=5,padx=10,row=1)
        ttk.Frame(inputmenu,width=400).grid()
        self.errtxt = tk.Label(inputmenu,fg="red")
        self.errtxt.grid(row=6,column=0)
        ttk.Button(inputmenu,text="Login",command=self.server_connect).grid(row=6,column=0,sticky="E")
        self.notebook.add(self,text="Login")
    
    def server_connect(self):
        try:
            if not(self.ip.get() in [None,""," ","\n"]):
                HOST=self.ip.get()
            PORT=int(self.iport.get())
            if "\n" in HOST:
                HOST=HOST.replace("\n","")
        except Exception as error:
            self.showerror(self.errtxt,f"{error}",35)
            return
        try:
            s=self.socket
            s.connect((HOST, PORT))
            self.Toolru.broadcast({"command":"socketOpen"})
            
        except Exception as error:
            self.showerror(self.errtxt,f"{error} for port:{PORT}",30)

    def showerror(self,label,text:str,linelim:int):
        text=[text[i:i+linelim] for i in range(0, len(text), linelim)]
        text="\n".join(text)
        label.config(text=text)
    
    def handle_command(self,command:dict):
        if command["command"]=="recvSocket":
            self.socket:socket.socket=self.Toolru.socket
        if command["command"]=="getWindow":
            return {"command":"recvWindow","args":[self,"cm-login"]}

def info():
    return {"prefix":"cm-login","mainclass":loginmenu}