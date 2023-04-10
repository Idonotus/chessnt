import tkinter as tk
from tkinter import ttk
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
class LoginPage(ttk.Frame):
    def __init__(self,master=None,main=None,nethandler=None) -> None:
        if not master:
            master=tk.Tk()
            master.title("PPPPPPPPPPPPP")
        self.main=main
        self.s=nethandler
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
        self.Suser=ttk.Entry(s,width=20)
        self.Suser.grid(row=1,pady=10,padx=10)
        ttk.Label(s,text="Password").grid(row=2)
        self.Spass=Password(s,20)
        self.Spass.grid(padx=10,pady=10,row=3)
        self.Sverif=Password(s,20)
        self.Sverif.grid(padx=10,pady=10,row=4)
        ttk.Button(s,text="Sign up",command=self.SignUp).grid(row=5)
        self.Sigerr=ttk.Label(s)
        self.Sigerr.grid(row=6)
        note.add(lt,text="Login")
        note.add(st,text="Sign up")
        self.pack()

    def SignUp(self):
        password=self.Spass.get()
        verification=self.Sverif.get()
        if password!=verification:
            self.showerror(self.Sigerr,"CredentialsError: Passwords dont match",20)
            return
        name=self.Suser.get()
        if not 3<=len(name)<=25:
            self.showerror(self.Sigerr,"CredentialsError: Username invalid",20)
            return
        elif not 1<=len(password)<=50:
            self.showerror(self.Sigerr,"CredentialsError: Password invalid",20)
            return
        if self.s:
            self.s.send(com="createUser",name=name,password=password)

    def Login(self):
        password=self.Lpass.get()
        name=self.Luser.get()
        valid=False
        if not 3<=len(name)<=25:
            self.showerror(self.Logerr,"CredentialsError: Username invalid",20)
        elif not 1<=len(password)<=50:
            self.showerror(self.Logerr,"CredentialsError: Password invalid",20)
        else:
            valid=True
        if not valid:
            return
        if self.s:
            com={"com":"loginUser","name":name,"pass":password}
            self.s.send(com)
            
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
        pass

if __name__=="__main__":
    c=LoginPage()
    tk.mainloop()