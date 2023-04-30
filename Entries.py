import tkinter as tk
from tkinter import ttk

class ErrLabel(ttk.Label):
    def showerror(self,text:str):
        if text==None or text=="":
            self.config(text="")
            return
        linelim=25
        newtext=[]
        line=""
        for word in text.split(" "):
            if len(line)<linelim:
                line+=word+" "
            else:
                newtext.append(line)
                line=word+" "
        newtext="\n".join(newtext)
        self.config(text=text)

class ValidateEntry(ttk.Entry):
    def __init__(self, master, widget = None, *, errcommand, errlabel=None, background = None, class_ = None, cursor = None, exportselection = None, font = None, foreground = None, justify = None, name = None, show = None, state = None, style = None, takefocus = None, textvariable = None, width: int = None, xscrollcommand = None) -> None:
        super().__init__(master, widget, background=background, class_=class_, cursor=cursor, exportselection=exportselection, font=font, foreground=foreground, justify=justify, name=name, show=show, state=state, style=style, takefocus=takefocus, textvariable=textvariable, width=width, xscrollcommand=xscrollcommand)
        self.config(validate="key", validatecommand=(self.register(self.validatecommand),"%P"))
        self.valid=False
        self.errcommand=errcommand
        self.errlabel=errlabel
        self.isvalid()
    
    def isvalid(self):
        self.validatecommand(self.get())
        return self.valid

    def validatecommand(self,S):
        r=self.errcommand(S)
        self.valid = not bool(r)
        if self.errlabel:
            self.errlabel.showerror(text=r)
        return True

class PasswordEntry(ttk.Frame):
    def __init__(self, master = None,width=2) -> None:
        super().__init__(master)
        self.show=tk.IntVar()
        f=ttk.Frame(self)
        f.grid(row=0,column=0)
        self.errlabel=ErrLabel(self,font=("Helvetica",10),foreground="red")
        self.errlabel.grid(row=1,column=0)
        self.entry=ValidateEntry(f,width=width-1,show="*",errcommand=self.validatePassword,errlabel=self.errlabel)
        self.entry.grid(column=0,row=0)
        
        ttk.Checkbutton(f,variable=self.show,command=self.toggleView).grid(column=1,row=0)

    def validatePassword(self,password):
        if len(password)>35:
            return "Password too short"
        if len(password)<5:
            return "Password too long"

    def isvalid(self):
        return self.entry.isvalid()

    def toggleView(self):
        if self.show.get():
            self.entry["show"]=""
        else:
            self.entry["show"]="*"
    def get(self):
        return self.entry.get()

class NameEntry(ttk.Frame):
    def __init__(self,master=None,width=1):
        super().__init__(master)
        self.errlabel=ErrLabel(self,font=("Helvetica",10),foreground="red")
        self.errlabel.grid(row=1,column=0)
        self.entry=ValidateEntry(self,width=width,errcommand=self.validateName,errlabel=self.errlabel)
        self.entry.grid(row=0,column=0)
    
    def isvalid(self):
        return self.entry.isvalid()

    def validateName(self,name):
        if len(name)>25:
            return "Name too long"
        elif len(name)<3:
            return "Name too short"
if __name__=="__main__":
    root=tk.Tk()
    PasswordEntry(root,10).pack()
    root.mainloop()