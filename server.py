import socket
import threading
import json
import sqlite3
import errno
database=sqlite3.connect("server.db",check_same_thread=False)
database.execute("CREATE TABLE IF NOT EXISTS users (name TEXT UNIQUE, auth INT, pass TEXT, originaddress TEXT)")
database.execute("CREATE TABLE IF NOT EXISTS addresses (addr TEXT UNIQUE, Userslotsleft INT)")
database.commit()
dataaccess=threading.Lock()
# --------TO DO---------
# +Login and leave
# 1.CHESS
# 2.CHAT
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
        self.bind((self.HOST,40000))
        self.PORT=self.getsockname()[1]
        print("Listening on ", self.getsockname())
        self.acceptingCon=True
        self.handler=handler
        self.listen()
        self.acceptCon()
        
    def acceptCon(self):
        while self.acceptingCon:
            c,addr=self.accept()
            c.sendall("aaaaa".encode())
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
            self.clientError(c,"l-"+response[1],"Login")
        dataaccess.acquire()
        response=database.execute("SELECT * FROM users WHERE (name=?,password=?)",(com["name"],com["pass"]))
        dataaccess.release()
        data=response.fetchone()
        if not data:
            self.clientError(c,"l-UserNotFound","Login")
            return
        data={"com":"Login","user":com["name"]}
        data=json.dumps(data)+"\0"
        c.sendall(data.encode())
        user.auth=data[1]
        user.name=data[0]
    def userSignUp(self,connection,user,com):
        c=connection
        addr=user.addr[0]
        response=self.validatecredentials(com)
        if not response[0]:
            self.clientError(c,"s-"+response[1],"Login")
            return
        response=self.createUser(1,com["name"],com["pass"],addr)
        if not response:
            self.clientError(c,"s-UserCreationError","Login")
            return
        dataaccess.acquire()
        database.execute("UPDATE addresses SET Userslotsleft=0 where addr=?",(addr,))
        database.commit()
        dataaccess.release()
        data={"com":"Login","user":com["name"]}
        data=json.dumps(data)+"\0"
        c.sendall(data.encode())
        user.auth=data[1]
        user.name=data[0]

    def validatecredentials(self,com)->tuple[bool,str,str]:
        if not("pass" in com and "name" in com):
            return (False,"BlankError")
        if not 1<=len(com["pass"])<=50:
            return (False,"LengthError")
        if not 3<=len(com["name"])<=25:
            return (False,"LengthError")
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
        
    def clientError(self,c,errortype,mod=None):
        if mod==None:
            mod="main"
        data={"com":"raiseError",
                "data":mod,
                "type":errortype}
        data=json.dumps(data)+"\0"
        c.sendall(data.encode())

    def leaveClient(self,user):
        pass

    def kickClient(self,user):
        user.c.close
class UserHandler:
    def __init__(self,c:socket.socket,addr,server:Server) -> None:
        self.user=None
        self.auth=None
        self.c=c
        self.addr=addr
        self.server=server
    def start(self):
        dataaccess.acquire()
        r=database.execute("SELECT Userslotsleft FROM addresses WHERE addr=?",(self.addr[0],))
        canCreateUser=0<r.fetchone()[0]
        database.rollback()
        dataaccess.release()
        c=self.c
        s=self.server
        del r
        data=""
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
                if not self.user:
                    if com["com"]=="createUser" and canCreateUser:
                        s.userSignUp(c,self,com)
                    if com["com"]=="loginUser":
                        s.login(c,self,com)
            data=coms[-1:][0]
if __name__=="__main__":
    s=Server(UserHandler)