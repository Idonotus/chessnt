import tkinter as tk
from tkinter import ttk
import socket
class Password(ttk.Frame):
    def __init__(self, master = None,width=0) -> None:
        super().__init__(master, width=width)
        self.show=tk.IntVar()
        self.entry=ttk.Entry(self,width=width-1,show="*")
        self.entry.grid(column=0,row=0)
        ttk.Checkbutton(self,variable=self.show,command=self.toggleView).grid(column=1,row=0)
    def toggleView(self):
        if self.show.get():
            self.entry["show"]=""
        else:
            self.entry["show"]="*"
    def get(self):
        return self.entry.get()
class ConnectPage(ttk.Frame):
    def __init__(self,master=None,main=None) -> None:
        if not master:
            master=tk.Tk()
        self.main=main
        self.s=None
        if main:
            self.s=main.socket
        super().__init__(master=master,height=700,width=1300)
        s=ttk.Style(self)
        s.configure(".",font=("Arial",11))
        note=ttk.Notebook(self,height=700,width=1300)
        note.pack(anchor="n")
        lt=ttk.Frame(note)
        lt.pack(anchor="center")
        l=ttk.Frame(lt)
        l.grid(row=0,column=0)
        lt.grid_columnconfigure(0,weight=1)
        lt.grid_rowconfigure(0,weight=1)
        ttk.Label(l,text="Username").grid(row=0)
        self.Luser=ttk.Entry(l,width=20)
        self.Luser.grid(row=1,pady=10,padx=10)
        ttk.Label(l,text="Password").grid(row=2)
        self.Lpass=Password(l,20)
        self.Lpass.grid(padx=10,pady=10,row=3)
        ttk.Button(l,text="Login").grid(row=4)
        note.add(lt,text="Login")
        self.pack()

    def Login(self):
        a=self.Lpass.get()

    def showerror(self,label,text:str,linelim:int):
        text=[text[i:i+linelim] for i in range(0, len(text), linelim)]
        text="\n".join(text)
        label.config(text=text)
if __name__=="__main__":
    c=ConnectPage()
    tk.mainloop()