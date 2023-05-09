import tkinter as tk
from tkinter import ttk
import socket
import threading
from WigExtras import ErrLabel
class ConnectPage(ttk.Frame):
    name="Pconnect"
    def __init__(self,master=None,main=None) -> None:
        if not master:
            master=tk.Tk()
        self.main=main
        super().__init__(master=master,height=700,width=1000)
        self.pack(fill="both",expand=True)
        inputmenu=ttk.Frame(self)
        inputmenu.place(anchor=tk.CENTER,relx=.5,rely=.5)
        self.ip = ttk.Entry(inputmenu,width=20)
        self.iport =ttk.Entry(width=5,master=inputmenu)
        ttk.Label(inputmenu,text="IP").grid(sticky="W",row=2)
        self.ip.grid(sticky="W",row=3,padx=10,pady=5)
        ttk.Label(inputmenu,text="Port").grid(sticky="W",row=4)
        self.iport.grid(sticky="W",pady=5,padx=10,row=5)
        ttk.Frame(inputmenu,width=400).grid()
        self.errtxt = ErrLabel(inputmenu)
        self.errtxt.grid(row=6,column=0)
        ttk.Button(inputmenu,text="Connect",command=self.server_connect).grid(row=6,column=0,sticky="E")
    def server_connect(self):
        self.errtxt.showerror()
        if not(self.ip.get() in [None,""," ","\n"]):
            HOST=self.ip.get()
        try:
            PORT=int(self.iport.get())
            if not 0<=PORT<=65535:
                raise ValueError
        except ValueError:
            self.errtxt.showerror(f"Not a valid port number",35)
            return
        try:
            if self.main:
                self.main.s.connect(HOST, PORT)
        except socket.error as error:
            self.errtxt.showerror(f"{error}",30)
            return
        if self.main:
            threading.Thread(
                target=self.main.s.listen,
                args=(self.main.handleCommand,)
            ).start()
            self.main.page("Plogin")

if __name__=="__main__":
    c=ConnectPage()
    tk.mainloop()