import tkinter as tk
from tkinter import ttk,font

class Username(ttk.Frame):
    def __init__(self, master,text:str) -> None:
        self.text=text
        super().__init__(master,style="User.TFrame")
        self.label=ttk.Label(self,text=text,style="Username.TLabel")
        self.label.pack(fill="x",expand=True)
        self.bind("<Configure>",lambda e: self.resizetext(e))
    
    def resizetext(self,e:tk.Event):
        if not self.label.cget("font"):
            s=font.nametofont("TkDefaultFont").actual()["size"]
        else:
            s=font.nametofont(self.label.cget("font")).actual()["size"]
        textwidth=self.winfo_width()*3/2
        possiblelen=int(textwidth//s)-1
        if possiblelen>=len(self.text):
            self.label.configure(text=self.text)
            return
        if possiblelen<=3:
            self.label.configure(text="...")
            return
        possiblelen-=3
        t=self.text[:possiblelen]+"..."
        self.label.configure(text=t)

class UserData(ttk.Frame):
    def __init__(self,master:tk.Widget,username="Dumbrguhhdhjkass",auth=False,possibleteams=(0,1),team=1,command=None):
        super().__init__(master=master)
        self.grid_columnconfigure(0,weight=1)
        self.user=Username(self,username)
        self.user.grid(row=0,column=0,sticky="WE")
        ttk.Label(self,text="Team").grid(row=0,column=1,padx=10,pady=6)
        self.command=command
        self.team=None
        self.setPossibleTeams(possibleteams)
        self.setAuth(auth)
        self.team.grid(row=0,column=2)

    def getUsername(self):
        return self.user.text

    def getTeam(self):
        if isinstance(self.team,ttk.Combobox):
            return self.team.get()
        else:
            return self.team.cget("text")
    
    def _teamchanged(self,e):
        if self.command:
            self.command(self.getTeam)
    
    def setAuth(self,auth:bool):
        if self.team:
            self.team.delete()
        if auth:
            self.team=ttk.Combobox(self,width=5,state="readonly")
            self.team.bind("<<ComboboxSelected>>",self._teamchanged)
            self.team["values"]=self.possibleteams
        else:
            self.team=ttk.Label(self,text="")
    
    def setPossibleTeams(self,choices):
        self.possibleteams=list(choices).copy()
        self.possibleteams.insert(0,"None")
        if isinstance(self.team,ttk.Combobox):
            self.team["values"]=choices
class ListBox(ttk.Frame):
    def __init__(self,master,height=0,width=0):
        super().__init__(master,height=height,width=width,style="Listbox.TFrame")
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(0,weight=1)
        self.c=tk.Canvas(self,background="Red")
        self.c.grid(row=0,column=0,sticky="NEWS")
        self.scroll=ttk.Scrollbar(self,command=self.c.yview)
        self.scroll.grid(row=0,column=1,sticky="NS")
        frame=ttk.Frame(self.c)
        self.c.create_window((0,0),window=frame,anchor="nw",tags="lframe")
        self.c.bind("<Configure>",lambda e: self.resizeconfig(e))
        frame.bind("<Configure>",lambda e: self.c.configure(scrollregion=self.c.bbox("all")))
        frame.grid_columnconfigure(0,weight=1)
        self.listframe=tk.Frame(frame,bg="red")
        self.listframe.grid_columnconfigure(0,weight=1)
        self.listframe.grid(row=0,sticky="WE")
        self.margin=ttk.Frame(frame)
        self.margin.grid(row=1)
        self.listchildren=[]
        frame.bind('<Enter>', self._bind_to_mousewheel)
        frame.bind('<Leave>', self._unbind_to_mousewheel)

    def _bind_to_mousewheel(self, event):
        self.c.bind_all("<MouseWheel>", self._on_mousewheel)
        self.c.bind_all("<Button-4>", self._on_mousewheel)
        self.c.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_to_mousewheel(self, event):
        self.c.unbind_all("<MouseWheel>")
        self.c.unbind_all("<Button-4>")
        self.c.unbind_all("<Button-5>")
    
    def resizeconfig(self,e=None):
        height=1
        if self.listframe.winfo_height()<self.c.winfo_height():
            height=self.c.winfo_height()-self.listframe.winfo_height()
        self.margin.config(height=height)
        self.c.itemconfig("lframe",width=self.c.winfo_width()-4)

    def insert(self,item:ttk.Frame,index=tk.END):
        if index==tk.END:
            index=len(self.listchildren)
        elif index>len(self.listchildren):
            index=len(self.listchildren)
        for i in range(len(self.listchildren)-1,index-1,-1):
            o:ttk.Frame=self.listchildren[i]
            o.grid_forget()
            o.grid(row=i+1,sticky="WE")
        item.grid(row=index,sticky="WE")
        self.listchildren.insert(index,item)
        self.resizeconfig()
    
    def remove(self,index=tk.END):
        if index==tk.END:
            index=len(self.listchildren)-1
        elif index>=len(self.listchildren):
            index=len(self.listchildren)-1
        self.listchildren.pop(index).destroy()
        for i in range(len(self.listchildren)-1,index-1,-1):
            o:ttk.Frame=self.listchildren[i]
            o.grid_forget()
            o.grid(row=i,sticky="WE")
        self.resizeconfig()
            
    def getmaster(self):
        return self.listframe

    def _on_mousewheel(self, event):
        if event.delta%120==0:
            delta=-1*(event.delta/120)
        if event.num==4:
            delta=-1
        elif event.num==5:
            delta=1
        self.c.yview_scroll(int(delta), "units")

class UserList(ListBox):
    def __init__(self, master, height=0, width=0):
        super().__init__(master, height, width)
        


    def insert(self, item: UserData, index=tk.END):
        if not isinstance(item,UserData):
            raise TypeError
        return super().insert(item, index)

    def findObj(self,name:str):
        for item in self.listchildren:
            if item.getUsername()==name:
                return item
    
    def setAuth(self,name:str,auth:bool):
        self.findObj(name).setAuth(auth)
    
    def removeName(self, name:str):
        return super().remove(self.listchildren.index(self.findObj(name)))

class ErrLabel(ttk.Label):
    def __init__(self, master= None, *, anchor = None, background = None, border = None, borderwidth = None, class_ = None, compound = None, cursor = None, font = None, foreground = None, image = None, justify = None, name = None, padding = None, relief = None, state = None, style = "Error.TLabel", takefocus = None, text = None, textvariable = None, underline = None, width = None, wraplength = None) -> None:
        super().__init__(master, anchor=anchor, background=background, border=border, borderwidth=borderwidth, class_=class_, compound=compound, cursor=cursor, font=font, foreground=foreground, image=image, justify=justify, name=name, padding=padding, relief=relief, state=state, style=style, takefocus=takefocus, text=text, textvariable=textvariable, underline=underline, width=width, wraplength=wraplength)
    def showerror(self,text:str="",linelim=25):
        if text==None or text=="":
            self.config(text="")
            return
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
    def __init__(self, master = None,width=None,text=None) -> None:
        super().__init__(master)
        self.show=tk.IntVar()
        f=ttk.Frame(self)
        f.grid(row=0,column=0)
        self.errlabel=ErrLabel(self,font=("Helvetica",10))
        self.errlabel.grid(row=1,column=0)
        self.entry=ValidateEntry(f,width=width,show="*",errcommand=self.validatePassword,errlabel=self.errlabel)
        self.entry.grid(column=0,row=0)
        ttk.Checkbutton(f,variable=self.show,command=self.toggleView).grid(column=1,row=0)

    def validatePassword(self,password):
        if len(password)>35:
            return "Password too long"
        if len(password)<5:
            return "Password too short"

    def isvalid(self):
        return self.entry.isvalid()

    def toggleView(self):
        if self.show.get():
            self.entry["show"]=""
        else:
            self.entry["show"]="*"
    def get(self):
        return self.entry.get()

class SecondaryPass(PasswordEntry):
    def __init__(self, master=None, width=None) -> None:
        self.entry2=None
        super().__init__(master, width)
        self.errlabel2=ErrLabel(self,font=("Helvetica",10))
        self.errlabel2.grid(row=3,column=0)
        self.entry2=ValidateEntry(self,width=width,show="*",errcommand=self.validate2ndPass,errlabel=self.errlabel2)
        self.entry2.grid(row=2,column=0)
    
    def validatePassword(self, password):
        r=super().validatePassword(password)
        if self.entry2:
            self.after(10,lambda: self.entry2.validatecommand(self.entry2.get()))
        return r

    def toggleView(self):
        if self.show.get():
            self.entry["show"]=""
            self.entry2["show"]=""
        else:
            self.entry["show"]="*"
            self.entry2["show"]="*"

    def validate2ndPass(self,password):
        if password!=self.entry.get():
            return "Passwords do not match"

    def isvalid(self):
        return self.entry.isvalid() and self.entry2.isvalid()
class NameEntry(ttk.Frame):
    def __init__(self,master=None,width=None):
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

    def get(self):
        return self.entry.get()
class LenPassEntry(PasswordEntry):
    def __init__(self, master=None, min:int=5 , max:int=35, width=None,text=None) -> None:
        if min>max:
            raise ValueError("Maximum is lower than minimum")
        self.min=min
        self.max=max
        super().__init__(master, width,text)
        
    def validatePassword(self, password):
        if len(password)>self.max:
            return "Password too long"
        if len(password)<self.min:
            return "Password too short"

class chatWidget(ttk.Frame):
    def __init__(self,master,sendcom=None) -> None:
        super().__init__(master)
        self.grid_rowconfigure(0,weight=1)
        self.grid_columnconfigure(0,weight=1)
        self.chathistory=tk.Listbox(self)
        self.chathistory.grid(row=0,column=0,columnspan=2,sticky="NEWS")
        self.chatentry=ttk.Entry(self)
        self.chatentry.grid(row=1,column=0,sticky="NEWS")
        self.grid_rowconfigure(0,weight=1)
        self.grid_columnconfigure(0,weight=1)
        chatExec=ttk.Button(self,text="Send")
        chatExec.grid(row=1,column=1)
    
    def chatupdate(self,hist:list) -> None:
        self.chathistory.delete(0,tk.END)
        for item in hist:
            self.chathistory.insert(tk.END,item)

if __name__=="__main__":
    root=tk.Tk()
    a=UserData(root,auth=True)
    a.pack(expand=True,fill="x")
    root.mainloop()