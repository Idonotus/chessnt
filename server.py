import socket
import threading
import json
import sqlite3
import errno
import logging
database=sqlite3.connect("server.db",check_same_thread=False)
database.execute("CREATE TABLE IF NOT EXISTS users (name TEXT UNIQUE, auth INT, pass TEXT, originaddress TEXT)")
database.execute("CREATE TABLE IF NOT EXISTS addresses (addr TEXT UNIQUE, Userslotsleft INT)")
database.commit()
dataaccess=threading.Lock()
# --------TO DO---------
# +Login and leave#
# 1.CHAT
# 2.CHESS
# 3.MODERATION
# 4.User stats
#
#
#
#
#
class Server(socket.socket):
    def __init__(self, handler, family: socket.AddressFamily  = socket.AF_INET, type: socket.SocketKind = socket.SOCK_STREAM) -> None:
        super().__init__(family, type)
        self.HOST=socket.gethostbyname(socket.gethostname())
        self.bind((self.HOST,40001))
        self.PORT=self.getsockname()[1]
        print("Listening on ", self.getsockname())
        self.acceptingCon=True
        self.handler=handler
        self.exequeue=[]
        threading.Thread(target=self.executioner,daemon=True).start()
        self.listen()
        self.acceptCon()

    def executioner(self):
        while True:
            if not len(self.exequeue)>0:
                continue
            com=self.exequeue[0]
            try:
                com["com"](*com["args"],**com["kwargs"])
            except Exception as e:
                logging.exception()
            finally:
                self.exequeue.pop(0)

    def addqueue(self,command,*args,**kwargs):
        self.exequeue.append({"com":command,"args":args,"kwargs":kwargs})

    def acceptCon(self):
        while self.acceptingCon:
            c,addr=self.accept()
            dataaccess.acquire()
            r=database.execute("SELECT count(*) FROM addresses WHERE addr=?",(addr[0],))
            if not r.fetchone()[0]:
                database.execute("INSERT INTO addresses (addr,Userslotsleft) VALUES (?,1)",(addr[0],))
                database.commit()
            dataaccess.release()
            h=self.handler(c,addr,self)
            threading.Thread(target=h.start).start()
            
    def login(self,connection,user,com):
        c=connection
        response=self.validatecredentials(com)
        if not response[0]:
            self.clientError(c,"l-"+response[1],"Plogin")
        dataaccess.acquire()
        response=database.execute("SELECT * FROM users WHERE name=? AND pass=?",(com["name"],com["pass"]))
        dataaccess.release()
        data=response.fetchone()
        
        if not data:
            self.clientError(c,"l-UserNotFound","Plogin")
            return
        user.auth=data[1]
        user.name=data[0]
        data={"com":"Login","user":com["name"],"mod":"UserAuth"}
        data=json.dumps(data)+"\0"
        c.sendall(data.encode())
        
    def userSignUp(self,connection,user,com):
        dataaccess.acquire()
        r=database.execute("SELECT Userslotsleft FROM addresses WHERE addr=?",(self.addr[0],))
        if 0<r.fetchone()[0]:
            self.clientError(c,"s-CreationUnavailable","Plogin")
        database.rollback()
        dataaccess.release()
        c=connection
        addr=user.addr[0]
        response=self.validatecredentials(com)
        if not response[0]:
            self.clientError(c,"s-"+response[1],"Plogin")
            return
        response=self.createUser(1,com["name"],com["pass"],addr)
        if not response:
            self.clientError(c,"s-UserCreationError","Plogin")
            return
        with dataaccess:
            database.execute("UPDATE addresses SET Userslotsleft=0 where addr=?",(addr,))
            database.commit()
        data={"com":"Login","user":com["name"],"mod":"UserAuth"}
        data=json.dumps(data)+"\0"
        c.sendall(data.encode())
        user.auth=data[1]
        user.name=data[0]

    def validatecredentials(self,com)->tuple[bool,str,str]:
        if not("pass" in com and "name" in com):
            return (False,"BlankError")
        if not 1<=len(com["pass"])<=50:
            return (False,"PassLengthError")
        if not 3<=len(com["name"])<=25:
            return (False,"NameLengthError")
        return (True,"CredentialsSucess")
    
    def createUser(self,auth,name,pasword,addr):
        dataaccess.acquire()
        try:
            database.execute("INSERT INTO users (name,auth,pass,originaddress) VALUES (?,?,?,?)",
                             (name,auth,pasword,addr)
                             )
            database.commit()
            success=True
        except sqlite3.IntegrityError:
            database.rollback()
            success=False
        dataaccess.release()
        return success
        
    def clientError(self,c,errortype,mod=None,**kwargs):
        if mod==None:
            mod="main"
        data={"com":"raiseError",
                "mod":mod,
                "type":errortype}
        data.update(kwargs)
        data=json.dumps(data)+"\0"
        c.sendall(data.encode())

    def leaveClient(self,user):
        pass

    def kickClient(self,user):
        user.c.close
class UserHandler:
    def __init__(self,c:socket.socket,addr,server:Server) -> None:
        self.user=None
        self.auth=-1
        self.c=c
        self.addr=addr
        self.server=server
    def start(self):
        c=self.c
        s=self.server
        data=""
        coms=[""]
        while True:
            try:
                data+=c.recv(1024).decode()
            except socket.error as error:
                if error.errno!= errno.ECONNRESET:
                    raise error
                s.leaveClient(self)
                break
            if data in [""]+coms[-1:]:
                s.leaveClient(self)
                break
            coms=data.split("\0")
            print(data)
            for com in coms[:-1]:
                com=json.loads(com)
                self.redirectCommand(com)
            data=coms[-1:][0]
    
    def redirectCommand(self,com):
        c=self.c
        s=self.server
        if not self.user and com["mod"]!="userauth":
            s.clientError(c,"NotAuth",reason="NoLogin")

        if com["mod"]=="userauth":
            if com["com"] in ["createUser","loginUser"]:
                if self.user:
                    s.clientError(c,"NotAuth",reason="LoggedIn")
                if com["com"]=="createUser":
                    s.addqueue(s.userSignUp,c,self,com)
                if com["com"]=="loginUser":
                    s.addqueue(s.login,c,self,com)
            #else:
                #
                
if __name__=="__main__":
    s=Server(UserHandler)