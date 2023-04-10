import socket

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
        self.open_sock=(host,port)