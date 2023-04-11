import socket
import json



class netClient:
    def __init__(self) -> None:
        self.socket=socket.socket()
        self.connectdata=None

    def listen(self,handlerfunc):
        data=""
        while True:
            try:
                data+=self.socket.recv(1024).decode()
            except socket.error:
                r=self.handleSuddenDisc()
                if r:
                    continue
                else:
                    break
            if data==sepdata:
                r=self.disconnect()
                break
            sepdata=data.split("\0")
            for msg in sepdata:
                handlerfunc(msg)
            data=data[-1:][0]

    def send(self,data:str):
        self.socket.sendall((data+"\0").encode())

    def assign(self,socket):
        self.socket=socket
    
    def handleSuddenDisc(self):
        self.socket.close()
        self.socket=socket.socket()
        if not self.connectdata:
            return False
        failure=True
        for _ in range(3):
            try:
                self.connect(self.connectdata)
                failure=False
                break
            except socket.error:
                #Ignoring them lol
                pass
        if failure:
            self.disconnect()
            return False
        return True

    def disconnect(self):
        self.socket.close()
        self.socket=socket.socket()
        self.connectdata=None

    def connect(self,host,port):
        self.socket.connect((host,port))
        self.connectdata=(host,port)

class appNetClient(netClient):
    def __init__(self,main=None) -> None:
        self.main=main
        super().__init__()
    def listen(self, handlerfunc):
        data=""
        while True:
            try:
                data+=self.socket.recv(1024).decode()
            except socket.error:
                r=self.handleSuddenDisc()
                if r:
                    continue
                else:
                    break
            if data==sepdata:
                r=self.disconnect()
                break
            sepdata=data.split("\0")
            for msg in sepdata:
                msg=json.loads(msg)
                handlerfunc(msg)
            data=data[-1:][0]
    
    def send(self, com:str|dict, **kwargs):
        if isinstance(com,dict) and len(kwargs)==0:
            data=json.dumps(com)
        else:
            kwargs["com"]=com
            data=json.dumps(kwargs)
        return super().send(data)

    def disconnect(self):
        if self.main:
            self.main.page("Pconnect")
        return super().disconnect()