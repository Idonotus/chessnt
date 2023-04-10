import socket
import threading
a="127.0.1.1"
p=40000
s=socket.socket()
s.connect((a,p))
def l(s):
    while True:
        a=s.recv(1024)
        print(a.decode())
threading.Thread(target=l,args=(s,)).start()
print("a")
while True:
    a=input("lol:")+"\0"
    s.sendall(a.encode())
