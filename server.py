import socket
import threading
import json
import sqlite3

database=sqlite3.connect("server.db")
database.execute("CREATE TABLE IF NOT EXISTS users (name TEXT UNIQUE, auth INT, password TEXT, originaddress TEXT)")
database.execute("CREATE TABLE IF NOT EXISTS addresses (addr TEXT UNIQUE, Userslotsleft INT)")
database.commit()
class Room:
    def __init__(self) -> None:
        self.users=[]
    
    def chat(self):
        pass
        

class Server(socket.socket):
    def __init__(self, family: socket.AddressFamily  = socket.AF_INET, type: socket.SocketKind = socket.SOCK_STREAM) -> None:
        super().__init__(family, type)
        self.HOST=socket.gethostbyname(socket.gethostname())
        self.bind((self.HOST,0))
        self.PORT=self.getsockname()[1]
        print("Listening on ", self.getsockname())
        self.acceptingCon=True
        self.listen()
        self.acceptCon()
    def acceptCon(self):
        while self.acceptingCon:
            c,addr=self.accept()
            r=database.execute("SELECT count(*) FROM addresses WHERE addr=?",(addr,))
            if not r.fetchone()[0]:
                database.execute("INSERT INTO addresses (addr,Userslotsleft) VALUES (?,1)",(addr,))

    def handleUser(self,c:socket.socket,addr):
        data=""
        userdata=None
        r=database.execute("SELECT Userslotsleft FROM addresses WHERE addr=?",(addr,))
        canCreateUser=0<r.fetchone()[0]
        while True:
            data+=c.recv(1024).decode()
            coms=data.split("\0")
            for com in coms[:-1]:
                com=json.loads(com)
                if not userdata:
                    if com["com"]=="createUser" and canCreateUser:
                        
                    
            data=coms[-1:]
    
    def validatecredentials(self,com)
        if not("pass" in com["args"] and "name" in com["args"]):
            {"com":"raiseError","args":{
                "data":"Username or password not found",
                "type":"createUserError"}}
            return False
        if not 1<=len(com["args"]["pass"])<=100:
            {"com":"raiseError","args":{
                "data":"Password must be between 100 and 1 characters",
                "type":"createUserError"
                }}
            return False
        if not 3<=len(com["args"]["name"])<=25:
            
            return False
    
    def returnError(self,c,errortype,msg):
        data={"com":"raiseError","args":{
                "data":msg,
                "type":errortype}}

    def createUser(self,c,auth,name,pasword,addr):
        try:
            database.execute("INSERT INTO addresses VALUES (name=?,auth=?,pass=?,originaddress=?)",
                             (name,auth,pasword,addr)
                             ) 
        except sqlite3.IntegrityError:
            self.returnError()
if __name__=="__main__":
    s=Server()