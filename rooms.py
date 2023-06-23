import Chess
import threading
import typing
from Chess.vectormath import vector
class Room:
    PAGENAME="Pr-null"
    def __init__(self, name:str, *, private:bool=False, password:str=None) -> None:
        self.name=name
        self.private=private
        self.password=password
        self.userlist={}

    def join(self,userobj):
        if userobj.name in self.userlist:
            return
        self.userlist[userobj.name]=userobj

    def leave(self,userobj):
        if userobj.name not in self.userlist:
            raise FileExistsError
        self.userlist.pop(userobj.name)
        
        com={"com":"RoomDisconnect","id":self.name,"mod":"room"}
    
    def inactive(self):
        return len(self.userlist)>=1

    def broadcast(self,com,name=None):
        for u in self.userlist:
            if u.name==name:
                continue
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
        
    def handlecommand(self,usr,com:dict):
        ...

class ChessRoom(Room):
    PAGENAME="Pr-chess"
    def __init__(self, name: str, *, private: bool = False, password: str = None) -> None:
        super().__init__(name, private, password)
        self.userteams={}
        self.logic=None
        self.running=False
        self.boardname="classic"
        self.userauths={}
        self.setting={
            "USERSSELFTEAMCHANGE":False
        }

    def join(self, userobj):
        super().join(userobj)
        name=userobj.name
        if name not in self.userauths:
            self.userauths[name]=1
        if userobj.auth!=1:
            self.userauths[name]=userobj.auth
        for user in self.userlist.values():
            user.send({"com":"userjoin","mod":self.PAGENAME,"user":name,"auth":self.AuthSetTeam(user,name)})
    
    def leave(self, userobj):
        super().leave(userobj)
        if userobj.name in self.userteams:
            self.userteams.pop(userobj.name)
        self.broadcast({"com":"userleave","mod":self.PAGENAME,"user":userobj.name})
    
    def AuthSetTeam(self,userobj,name):
        if self.running:
            return False
        if userobj.auth<1:
            return False
        if userobj.name!=name and userobj.auth==1:
            return False
        if userobj.auth==1 and not self.setting["USERSELFTEAMCHANGE"]:
            return False
        return True

    def startGame(self,data):
        sizedata=data["dim"]
        teamcount=data["numteams"]
        board=data["boarddata"]
        self.torder=data["turnorder"]
        self.logic=Chess.Logic.Logic.genboard(teamcount,sizedata,board)
        self.turnorder=Chess.turngen(data["turnorder"])
        self.turn=next(self.turnorder)
        self.logic.teamturn=self.turn
        self.running=True
        c={"com":"loadboard","data":self.exportBoard(),"mod":self.PAGENAME}
        self.broadcast(c)
    
    def AuthMove(self, userobj, pos):
        p=self.logic.getpiece(pos=pos)
        if userobj.name not in self.userteams:
            return False
        if p.team not in self.userteams[userobj.name]:
            return False
        return True

    def makeMove(self, userobj, pos1,pos2):
        if not self.running:
            return
        if not self.logic.ispiece(pos=pos1):
            return
        if not self.authmove(userobj,pos1):
            return
        if not self.logic.canmove(pos1,pos2):
            return
        r=self.logic.movepiece(pos1,pos2)
        if not r:
            return
        self.broadcast({"com":"loadmove","mod":self.PAGENAME,"dif":r})
        self.endturn()

    def endturn(self):
        self.turn=next(self.turnorder)
        self.logic.teamturn=self.turn

    def handlecommand(self,usr,com:dict):
        match com:
            case {"com":"getauth","action":"flowcontrol",**_u}:
                c={"com":"setauth","action":"flowcontrol","mod":self.PAGENAME,"auth":self.userauths[usr.name]>=3}
                usr.send(c)
            case {"com":"getboard",**_u} if self.running:
                r=self.exportBoard(self)
                com={"com":"loadboard","data":r,"mod":self.PAGENAME}
                usr.send(com)
            case {"com":"getusers",**_u}:
                r=self.exportUserData(usr)
                com={"com":"loaduser","data":r,"mod":self.PAGENAME}
                usr.send(com)
            case {"com":"setteam","user":name,"team":team,**_u} if not self.running:
                self.setTeam(usr,name,team)
            case {"com":"makemove","pos1":pos1,"pos2":pos2,**_u} if self.running:
                pos1=vector.fromtuple(pos1)
                pos2=vector.fromtuple(pos2)
                self.makeMove(usr,pos1,pos2)
            case {"com":"getmoves","piecepos":pos,**_u} if self.running:
                pos=vector.fromtuple(pos)
                r=self.getpossiblemoves(pos)
                c={"com":"highlightmoves","mod":self.PAGENAME,"tiles":r,"pos":pos}
                usr.send(c)

    def getpossiblemoves(self,pos):
        if not self.running:
            return
        p=self.logic.getpiece(pos=pos)
        if not p:
            return
        return [m.intcoords() for m in p.getallmoves()]

    def setTeam(self,usr,name,team):
        if not self.AuthSetTeam(usr,name):
            return
        self.userteams[name]=team
        self.broadcast({"com":"teamChanged","name":name,"team":team,"mod":self.PAGENAME})

    def exportBoard(self,):
        if not self.running:
            r=Chess.Stateloader.getBoard(self.boardname)
            r["running"]=False
            return 
        d=self.logic.data
        dup=[]
        for x,strip in enumerate(d):
            dup.append([])
            for y,p in enumerate(strip):
                if isinstance(p,Chess.logic.Piece):
                    p=p.export()
                dup[x].append(p)
        bd={
            "dim":[self.logic.WIDTH,self.logic.HEIGHT],
            "turnorder":self.turnorder,
            "numteams":2,
            "boarddata":dup,
            "running":True
        }
        return bd
    
    def exportUserData(self,userobj):
        d=[]
        for n in self.userlist.keys:
            if n not in self.userteams:
                d.append((n,self.AuthSetTeam(userobj,n),None))
            else:
                d.append((n,self.AuthSetTeam(userobj,n),self.userteams[n]))
        return d
        

class RoomServer:
    def __init__(self) -> None:
        self.roomindex:typing.Mapping[str,Room]={}
        self.userindex={}

    def createRoom(self, roomcls:Room, Id, **kwargs) -> Room:
        if not isinstance(roomcls,Room):
            raise TypeError("NOT A ROOM YOU ***********************")
        if Id not in self.roomindex:
            r:Room=roomcls(Id, **kwargs)
            self.roomindex[Id]=r
            return r
        else:
            raise FileExistsError

    def joinRoom(self,userobj,roomId:str,password=None):
        if roomId not in self.roomindex:
            raise FileNotFoundError
        if userobj.name in self.userindex:
            if not self.userindex[userobj.name]:
                raise FileExistsError
        room=self.roomindex[roomId]
        if room.AuthJoin(password):
            self.userindex[userobj.name]=roomId
            self.roomindex[roomId].join(userobj)
        else:
            raise EnvironmentError

    def leaveRoom(self,userobj,roomId):
        if userobj.name not in self.userindex:
            return
        self.userindex.pop(userobj.name)
        self.roomindex[roomId].leave(userobj)
    
    def broacast(self,roomId,com,user=None):
        if not (isinstance(user,(str)) or not user):
            user=user.name
        if roomId not in self.roomindex:
            return
        self.roomindex[roomId].broadcast(com,user)
    
    def destroy(self,roomId):
        pass
    
    def send(self,roomId,com,user):
        if roomId not in self.roomindex:
            return
        self.roomindex[roomId].send(com,user.name)

    def usercommands(self,user,com):
        match com:
            case {"forwardtoroom":True,"com":_,**_u}:
                if user.name not in self.userindex:
                    user.clientError("NotInRoom","main")
                if not self.userindex[user.name]:
                    user.clientError("NotInRoom","main")
                self.roomindex[self.userindex[user.name]].handlecommand(user,com)
            case {"com":"createroom","roomname":roomname,"roompass":roompass,**_u}:
                try:
                    r:ChessRoom=self.createRoom(ChessRoom,roomname,password=roompass)
                    r.userauths[user.name]=3
                    user.send({"com":"joinedroom","mod":"Proomsel","type":self.roomindex[roomname].pagename})
                except FileExistsError:
                    user.clientError("RoomExists","Proomsel")
            case {"com":"joinroom","roomname":roomname,"roompass":roompass,**_u}:
                roomname=com["roomname"]
                roompass=com["roompass"]
                try:
                    self.joinRoom(user,roomname,roompass)
                    user.send({"com":"joinedroom","mod":"Proomsel","type":self.roomindex[roomname].pagename})
                except (EnvironmentError, FileNotFoundError, FileExistsError):
                    user.clientError("AuthDeny","Proomsel")
            case {"com":"getrooms",**_u}:
                visiblerooms=[
                {"name":room.name,"password":bool(room.password)}
                for room in self.roomindex.values() if room.AuthSee
                ]
                com={"com":"refreshrooms","roomarray":visiblerooms,"mod":"Proomsel"}
                user.send(com)
