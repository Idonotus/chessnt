import socket
import json
import logging
import time
import threading

class netClient:
    def __init__(self) -> None:
        self.socket=socket.socket()
        self.connectdata=None
        self.online=False
        self.queue=[]
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
                threading.Thread(target=handlerfunc,args=(msg,)).start()
            data=data[-1:][0]

    def send(self,data:str):
        if not self.online:
            self.queue.append(data)
            return
        self.socket.sendall((data+"\0").encode())

    def assign(self,socket):
        self.socket=socket
    
    def handleSuddenDisc(self):
        self.online=False
        logging.info("Lost connection: attemping reconnect")
        self.socket.close()
        self.socket=socket.socket()
        if not self.connectdata:
            return False
        failure=True
        wt=1
        for x in range(10):
            try:
                self.connect(*self.connectdata)
                logging.debug(f"Attempt {x}:success")
                logging.info("Reconnect sucessful")
                self.online=True
                failure=False
                self.handleQueue()
                break
            except socket.error:
                time.sleep(wt)
                wt+=1
                logging.debug(f"Attempt {x}:failed")
                #Ignoring them lol
                
        if failure:
            logging.info("Failed to reconnect")
            self.disconnect()
            return False
        return True

    def disconnect(self):
        self.socket.close()
        self.socket=socket.socket()
        self.connectdata=None
        self.online=False

    def handleQueue(self):
        q=self.queue
        self.queue=[]
        for data in q:
            self.send(data)
            if data in self.queue:
                logging.warn("Queue not cleared")
                self.queue=q
                break

    def connect(self,host,port):
        self.socket.connect((host,port))
        self.connectdata=(host,port)
        self.online=True

class appNetClient(netClient):
    def __init__(self,main=None) -> None:
        self.main=main
        super().__init__()
    def listen(self, handlerfunc):
        data=""
        sepdata=[""]
        while True:
            try:
                data+=self.socket.recv(1024).decode()
                logging.debug(f"Recieved data:{data}")
            except socket.error:
                r=self.handleSuddenDisc()
                if r:
                    continue
                else:
                    break
            if data==sepdata[-1:]:
                r=self.disconnect()
                break
            sepdata=data.split("\0")
            for msg in sepdata[:-1]:
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