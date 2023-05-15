import Chess
import threading
class Room:
    def __init__(self, name:str, *, private:bool=False, password:str=None) -> None:
        self.name=name
        self.private=private
        self.password=password
        self.userlist={}

    def join(self,userobj):
        self.userlist[userobj.name]=userobj

    def leave(self,userobj):
        if userobj.name not in self.userlist:
            return
        self.userlist.pop(userobj.name)
        
        com={"com":"RoomDisconnect","id":self.name,"mod":"room"}
    
    def inactive(self):
        return len(self.userlist)>=1

    def broadcast(self,com,name=None):
        for u in self.userlist:
            if u.name!=name:
                u.send(com)
    
    def close(self):
        for user in self.userlist.items():
            c=user[1].c
            com={"com":"RoomDisconnect","id":self.name,"mod":"room"}

    def sendTo(self,com,name):
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
        self.userteams={}
        self.logic=None
        self.running=False

    def startGame(self,data):
        sizedata=data["size"]
        teamcount=data["teams"]
        self.logic=Chess.logic.Logic(sizedata[0],sizedata[1],teamcount)
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
        self.turnorder=Chess.turngen(data["turnorder"])
        self.turn=next(self.turnorder)
        self.logic.teamturn=self.turn
        self.running=True
    
    def authmove(self, userobj, pos):
        p=self.logic.getpiece(pos=pos)
        if userobj.name not in self.userteams:
            return False
        if p.team not in self.userteams[userobj.name]:
            return False
        return True


    def make_move(self,userobj,pos1,pos2):
        if not self.running:
            return
        if not self.logic.ispiece(pos=pos1):
            return
        if not self.authmove(userobj,pos1):
            return
        if not self.logic.canmove(pos1,pos2):
            return
        r=self.logic.movepiece(pos1,pos2)
        if r is None:
            return
        self.gui.applychanges(r)
        self.endturn()

    def endturn(self):
        self.turn=next(self.turnorder)
        self.logic.teamturn=self.turn

    def handlecommand(self,):
        if self.running:
            pass
        else:
            pass
class RoomServer:
    def __init__(self) -> None:
        self.roomindex={}
        self.userindex={}

    def createRoom(self, roomcls:Room, Id, **kwargs):
        if not isinstance(roomcls,Room):
            raise TypeError("NOT A ROOM YOU ***********************")
        if Id not in self.roomindex:
            self.roomindex[Id]=roomcls(Id, **kwargs)
        else:
            raise FileExistsError

    def joinRoom(self,userobj,roomId:str,password=None):
        if userobj.name not in self.userindex:
            self.userindex[userobj.name]=[]
        if roomId not in self.roomindex:
            raise FileNotFoundError
        room=self.roomindex[roomId]
        if room.AuthJoin(password):
            self.userindex[userobj.name]=roomId
            self.roomindex[roomId].join(userobj)
        else:
            raise EnvironmentError

    def leaveRoom(self,userobj,roomId):
        if userobj.name not in self.userindex:
            return
        self.userindex[userobj.name]=""
        self.roomindex[roomId].leave(userobj)
    
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

    def room_usercommands(self,user,com):
        #createroom
        #joinroom
        #getrooms
        match com["com"]:
            case "createroom":
                roomname=com["roomname"]
                roompass=com["roompass"]
                try:
                    self.createRoom(Room,roomname,password=roompass)
                    user.send({"com":"joinedroom","mod":"Prromsel","type":"Simple"})
                except FileExistsError:
                    user.clientError("RoomExists","Proomsel")
            case "joinroom":
                roomname=com["roomname"]
                roompass=com["roompass"]
                try:
                    self.joinRoom(user,roomname,roompass)
                except EnvironmentError or FileNotFoundError:
                    user.clientError("AuthDeny","Proomsel")
            case "getrooms":
                visiblerooms=[
                {"name":room.name,"password":bool(room.password)}
                for room in self.roomindex.values() if room.AuthSee
                ]
                com={"com":"refreshrooms","roomarray":visiblerooms,"mod":"Proomsel"}
                user.send(com)
