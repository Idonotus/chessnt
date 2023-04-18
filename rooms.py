import Chess
import threading
class Room:
    def __init__(self, name:str, *, private:bool=False, password:str=None) -> None:
        self.name=name
        self.private=private
        self.password=password
        self.userlist={}
        self.roomlock=threading.Lock()

    def join(self,userobj):
        with self.roomlock:
            self.userlist[userobj.name]=userobj

    def leave(self,userobj):
        with self.roomlock:
            if userobj.name not in self.userlist:
                return
            self.userlist.pop(userobj.name)
    
    def inactive(self):
        return len(self.userlist)>=1

    def broadcast(self,com,name=None):
        with self.roomlock:
            for u in self.userlist:
                if u.name!=name:
                    u.send(com)
    
    def sendTo(self,com,name):
        with self.roomlock:
            if name not in self.userlist:
                return
            self.userlist[name].send(com)

    def AuthSee(self):
        return not self.private

    def AuthJoin(self,password):
        if self.password:
            return self.password==password
        else:
            return True

class chessRoom(Room):
    def __init__(self, name: str, *, private: bool = False, password: str = None) -> None:
        super().__init__(name, private, password)
        self.logic=None

    def startGame(self,data):
        sizedata=data["size"]
        teamcount=data["teams"]
        self.logic=Chess.Logic.GameLogic.Logic(sizedata[0],sizedata[1],teamcount)
        for y,row in enumerate(data["board"].split("|nr|")):
            x=0
            for tile in row.split(","):
                places=1
                p=tile
                if "*" in tile:
                    tile=tile.split("*")
                    p=tile[0]
                    places=int(tile[1])
                for _ in range(places):
                    if p[0]=="o":
                        x+=1
                        continue
                    self.logic.addpiece(Chess.pieces[p[0]],x,y,int(p[1]))
                    x+=1
        self.turnorder=Chess.conductor.genturn(data["turnorder"])
        self.turn=next(self.turnorder)
    
    def make_move(self,team):

        self.turn=next(self.turnorder)

class RoomServer:
    def __init__(self) -> None:
        self.roomlock=threading.Lock()
        self.roomindex={}
        self.userindex={}

    def createRoom(self, roomcls:Room, Id, **kwargs):
        with self.roomlock:
            if not isinstance(roomcls,Room):
                raise TypeError("NOT A ROOM YOU ***********************")
            if Id not in self.roomindex:
                self.roomindex[Id]=roomcls(Id, **kwargs)
            else:
                raise FileExistsError

    def join(self,userobj,roomId:str):
        if userobj.name not in self.userindex:
            self.userindex[userobj.name]=[]
        self.userindex[userobj.name].append(roomId)
        self.roomindex[roomId].join(userobj)

    def leave(self,userobj,roomId):
        with self.roomlock:
            if userobj.name not in self.userindex:
                return
            userrooms:list=self.userindex[userobj.name]
            if roomId in userrooms:
                userrooms.remove(roomId)
            self.roomindex[roomId].leave(userobj)

    def leaveall(self,userobj):
        if userobj.name not in self.userindex:
            return
        userrooms:list=self.userindex[userobj.name]
        for roomId in userrooms:
            self.roomindex[roomId].leave(userobj)
        self.userindex.pop(userobj.name)
    
    def broacast(self,roomId,com,user=None):
        if not (isinstance(user,(str)) or not user):
            user=user.name
        if roomId not in self.roomindex:
            return
        self.roomindex[roomId].broadcast(com,user.name)
    
    def destroy(self,roomId):
        pass
    
    def send(self,roomId,com,user):
        if roomId not in self.roomindex:
            return
        self.roomindex[roomId].send(com,user.name)
    
