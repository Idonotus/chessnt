import tkinter as tk
from tkinter import ttk,messagebox
from WigExtras import PasswordEntry,NameEntry,SecondaryPass
ERRORDEF = {
    "CreationUnavailable":"Already created a user",
    "UserCreationError":"User already exists",
    "BlankError":"Username or password not entered",
    "PassLengthError":"Passwords gave to be between 1",
    "NameLengthError":"Username or password too long or sgor",
    "UserNotFound":"User not found"
}
class UserAuth:
    def __init__(self,main) -> None:
        self.main=main
    def handleCommand(self,com):
        if com["com"]=="Login":
            self.main.page("main")

class LoginPage(ttk.Frame):
    name="Plogin"
    def __init__(self,master=None,main=None) -> None:
        if not master:
            master=tk.Tk()
            master.title("PPPPPPPPPPPPP")
        self.main=main
        if main:
            main.createBackProc("UserAuth",UserAuth(main))
            self.s=main.s
        else:
            self.s=None
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
        self.Luser=NameEntry(l,width=20)
        self.Luser.grid(row=1,pady=10,padx=10)
        ttk.Label(l,text="Password").grid(row=2)
        self.Lpass=PasswordEntry(l,20)
        self.Lpass.grid(padx=10,pady=10,row=3)
        ttk.Button(l,text="Login",command=self.Login).grid(row=4)
        self.Logerr=ttk.Label(l)
        self.Logerr.grid(row=6)
        st=ttk.Frame(note)
        st.pack(anchor="center")
        s=ttk.Frame(st)
        s.grid(row=0,column=0)
        st.grid_columnconfigure(0,weight=1)
        st.grid_rowconfigure(0,weight=1)
        ttk.Label(s,text="Username").grid(row=0)
        self.Suser=NameEntry(s,width=20)
        self.Suser.grid(row=1,pady=10,padx=10)
        ttk.Label(s,text="Password").grid(row=2)
        self.Spass=SecondaryPass(s,20)
        self.Spass.grid(padx=10,pady=10,row=3)
        ttk.Button(s,text="Sign up",command=self.SignUp).grid(row=5)
        self.Sigerr=ttk.Label(s)
        self.Sigerr.grid(row=6)
        note.add(lt,text="Login")
        note.add(st,text="Sign up")
        self.pack()

    def SignUp(self):
        if not (self.Spass.isvalid() and self.Suser.isvalid()):
            return
        password=self.Spass.get()
        name=self.Suser.get()
        if self.s:
            com={"com":"createUser","name":name,"pass":password,"mod":"userauth"}
            self.s.send(com)

    def Login(self):
        if not (self.Lpass.isvalid() and self.Luser.isvalid()):
            return
        password=self.Lpass.get()
        name=self.Luser.get()
        if self.s:
            com={"com":"loginUser","name":name,"pass":password,"mod":"userauth"}
            self.s.send(com=com)
            
    def showerror(self,label,text:str,linelim:int):
        newtext=[]
        line=""
        for word in text.split(" "):
            if len(line)<linelim:
                line+=word+" "
            else:
                newtext.append(line)
                line=word+" "
        newtext="\n".join(newtext)
        label.config(text=text)
    
    def handleCommand(self,com):
        if com["com"]=="raiseError":
            t=com["type"]
            t=t.split("-")
            if t[1] not in ERRORDEF:
                return
            messagebox.showerror(message=f"{ERRORDEF[t[1]]}")




if __name__=="__main__":
    c=LoginPage()
    tk.mainloop()