import socket
import threading
import json
import sqlite3
import errno
import logging
import os
import queue
import dataclasses
import rooms
logging.basicConfig(format="[%(levelname)s] %(message)s",level=logging.DEBUG)
database=sqlite3.connect("server.db",check_same_thread=False)

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

@dataclasses.dataclass(order=True)
class QueuedThread:
    priority: int
    item:threading.Thread = dataclasses.field(compare=False)



class UserDataServer:
    def __init__(self,db:sqlite3.Connection,dblock=threading.Lock()) -> None:
        self.db=db
        self.dblock=dblock
        self.db.execute("CREATE TABLE IF NOT EXISTS users (name TEXT UNIQUE, auth INT, pass TEXT, originaddress TEXT)")
        self.db.execute("CREATE TABLE IF NOT EXISTS addresses (addr TEXT UNIQUE, Userslotsleft INT)")
        self.db.commit()

    def createUser(self,auth,name,pasword,addr):
        with self.dblock:
            try:
                self.db.execute("INSERT INTO users (name,auth,pass,originaddress) VALUES (?,?,?,?)",
                                (name,auth,pasword,addr)
                                )
                self.db.commit()
                success=True
            except sqlite3.IntegrityError:
                self.db.rollback()
                success=False
        return success
    
    def userjoined(self,addr):
        with self.dblock:
            r=self.db.execute("SELECT count(*) FROM addresses WHERE addr=?",(addr,))
            if not r.fetchone()[0]:
                self.db.execute("INSERT INTO addresses (addr,Userslotsleft) VALUES (?,1)",(addr,))
                self.db.commit()
    
    def getuserslots(self,addr):
        with self.dblock:
            r=self.db.execute("SELECT Userslotsleft FROM addresses WHERE addr=?",(addr,))
            self.db.rollback()
        return int(r.fetchone()[0])
    
    def decrementslots(self,addr):
        c=self.getuserslots(addr)
        with self.dblock:
            self.db.execute("UPDATE addresses SET Userslotsleft=? where addr=?",(c-1,addr))
            self.db.commit()
    
    def getuser(self,name:str,password:str):
        if not self.userindb(name,password):
            raise FileNotFoundError
        with self.dblock:
            response=self.db.execute("SELECT * FROM users WHERE name=? AND pass=?",(name,password))
        return response.fetchone()

    def userindb(self,name:str,password:str):
        with self.dblock:
            response=self.db.execute("SELECT * FROM users WHERE name=? AND pass=?",(name,password))
        return bool(response.fetchone())

class ExeQueuetioner:
    def __init__(self) -> None:
        self.exequeue=queue.PriorityQueue()
    def start(self):
        while True:
            com:QueuedThread=self.exequeue.get(block=True)
            try:
                com.item.run()
            except Exception:
                logging.exception(msg="Qerror")
            finally:
                self.exequeue.task_done()

    def addqueue(self,thread:threading.Thread,priority=1):
        self.exequeue.put(QueuedThread(priority,thread))
        return thread.join() 
class Server(socket.socket, rooms.RoomServer):
    def __init__(self, handler, family: socket.AddressFamily  = socket.AF_INET, type: socket.SocketKind = socket.SOCK_STREAM) -> None:
        super().__init__(family, type)
        self.HOST=socket.gethostbyname(socket.gethostname())
        self.bind((self.HOST,40000))
        self.PORT=self.getsockname()[1]
        print("Listening on ", self.getsockname())
        self.acceptingCon=True
        self.handler=handler
        self.roomindex={}
        self.userindex={}
        self.dbserver=UserDataServer(database,dataaccess)
        self.exe=ExeQueuetioner()
        self.roomserver=rooms.RoomServer()
        threading.Thread(target=self.exe.start,daemon=True).start()
        self.listen()
        self.acceptCon()

    def acceptCon(self):
        while self.acceptingCon:
            c,addr=self.accept()
            self.dbserver.userjoined(addr[0])
            h=self.handler(c,addr,self)
            threading.Thread(target=h.start,daemon=True).start()
            
    def login(self,user,com):
        response=self.validatecredentials(com)
        if not response[0]:
            user.clientError("l-"+response[1],"Plogin")

        if not self.dbserver.userindb(com["name"],com["pass"]):
            user.clientError("l-UserNotFound","Plogin")
            return

        
        
    def userSignUp(self,user,com):
        addr=user.addr[0]
        c=self.dbserver.getuserslots(addr)
        if not c:
            user.clientError("s-CreationUnavailable","Plogin")
            return
        response=self.validatecredentials(com)
        if not response[0]:
            user.clientError("s-"+response[1],"Plogin")
            return
        response=self.dbserver.createUser(1,com["name"],com["pass"],addr)
        if not response:
            user.clientError("s-UserCreationError","Plogin")
            return
        self.dbserver.decrementslots(addr)
        data={"com":"Login","user":com["name"],"mod":"UserAuth"}
        user.send(data)

    def senduserdata(self,user,name,password):
        data=self.dbserver.getuser(name,password)
        user.auth=data[1]
        user.name=data[0]
        data={"com":"Login","user":name,"mod":"UserAuth"}
        user.send(data)

    def validatecredentials(self,com):
        if not("pass" in com and "name" in com):
            return (False,"BlankError")
        if not 1<=len(com["pass"])<=50:
            return (False,"PassLengthError")
        if not 3<=len(com["name"])<=25:
            return (False,"NameLengthError")
        return (True,"CredentialsSucess")
    

        
    
    def leaveClient(self,user):
        pass

    def kickClient(self,user):
        user.c.close()
class UserHandler:
    def __init__(self,c:socket.socket,addr,server:Server) -> None:
        self.user=None
        self.auth=-1
        self.c=c
        self.addr=addr
        self.server=server
        self.clientError("CryBoutIt")

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
    
    def send(self,data):
        if isinstance(data,dict):
            data=json.dumps(data)
        data+="\0"
        self.c.sendall(data.encode())
    
    def redirectCommand(self,com):
        c=self.c
        s=self.server
        self.q=self.server.exe
        if not self.user and com["mod"]!="userauth":
            self.clientError(c,"NotAuth",reason="NoLogin")

        if com["mod"]=="userauth":
            if com["com"] in ["createUser","loginUser"]:
                if self.user:
                    self.clientError(c,"NotAuth",reason="LoggedIn")
                if com["com"]=="createUser":
                    self.q.addqueue(s.userSignUp,self,com)
                if com["com"]=="loginUser":
                    self.q.addqueue(s.login,self,com)
        if com["mod"]=="rooms":
            self.q.addqueue(s.roomserver.usercommands,self,com)
    
    def clientError(self,errortype,mod="main", queue=False,**kwargs):
        data={"com":"raiseError",
                "mod":mod,
                "type":errortype}
        data.update(kwargs)
        if queue:
            data["cause"]=self.q.fetchlast()
        data=json.dumps(data)+"\0"
        self.c.sendall(data.encode())

if __name__=="__main__":
    s=Server(UserHandler)