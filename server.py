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
        del r
        while True:
            data+=c.recv(1024).decode()
            coms=data.split("\0")
            for com in coms[:-1]:
                com=json.loads(com)
                if not userdata:
                    if com["com"]=="createUser" and canCreateUser:
                        self.userSignUp(c,com,addr)
                        
                    
            data=coms[-1:]
        
    def userSignUp(self,c,com,addr):
        response=self.validatecredentials()
        if not response[0]:
            self.returnError(c,response[1],response[2])
            return
        response=self.createUser(c,1,com["name"],com["pass"],addr)
        if not response:
            self.returnError(c,"UserExistsError","The user being created already exists")
        else:
            data={"com":"Login","user":com["name"]}
            data=json.dumps(data)+"\0"
            c.sendall(data.encode())

    def validatecredentials(self,com)->tuple[bool,str,str]:
        if not("pass" in com and "name" in com):
            return (False,"CredentialsError","Username or Password missing")
        if not 1<=len(com["pass"])<=100:
            return (False,"CredentialsError","Password too long")
        if not 3<=len(com["name"])<=25:
            return (False,"CredentialsError","Username too long")
        return (True,"CredentialsSucess","Requirements met")
    
    def returnError(self,c,errortype,msg):
        data={"com":"raiseError",
                "data":msg,
                "type":errortype}
        data=json.dumps(data)+"\0"
        c.sendall(data.encode())

    def createUser(self,auth,name,pasword,addr):
        try:
            database.execute("INSERT INTO addresses VALUES (name=?,auth=?,pass=?,originaddress=?)",
                             (name,auth,pasword,addr)
                             )
            database.commit()
            return True
        except sqlite3.IntegrityError:
            return False
if __name__=="__main__":
    s=Server()