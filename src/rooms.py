import Chess
import threading
import typing
import logging
from Chess.vectormath import vector
class Room:
    PAGENAME="Pr-null"
    def __init__(self, name:str, *, private:bool=False, password:str=None) -> None:
        self.name=name
        self.private=private
        self.password=password
        self.userauths={}
        self.userlist={}
    
    def setAuth(self,user,value:int):
        if not isinstance(value,int):
            raise TypeError
        self.userauths[user.name]=value
    
    def join(self,userobj):
        if userobj.name in self.userlist:
            return
        self.userlist[userobj.name]=userobj
        name=userobj.name
        if name not in self.userauths:
            self.userauths[name]=1
        if userobj.auth!=1:
            self.userauths[name]=userobj.auth

    def leave(self,userobj):
        if userobj.name not in self.userlist:
            raise FileExistsError
        self.userlist.pop(userobj.name)
        com={"com":"leftroom","mod":"stateHandler"}
        userobj.send(com)
        com={"com":"userleave","name":userobj.name}
        self.broadcast(com)
    
    def inactive(self):
        return len(self.userlist)<=0

    def broadcast(self,com,name=None):
        if "mod" not in com:
            com["mod"]=self.PAGENAME
        for uname,u in self.userlist.items():
            if uname==name:
                continue
            u.send(com)
    
    def close(self):
        self.broadcast({"com":"leftroom","mod":"stateHandler"})

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
    
    def canPersist(self):
        if not self.inactive():
            return True
        if hasattr(self,"persist"):
            if type(self.persist)==bool:
                return self.persist
        return False

class SelRoom(Room):
    PAGENAME="Pr-sel"
    persist=True

class ChessRoom(Room):
    PAGENAME="Pr-chess"
    def __init__(self, name: str, *, private: bool = False, password: str = None) -> None:
        super().__init__(name, private=private, password=password)
        self.userteams={}
        self.logic=None
        self.running=False
        self.boardname="classic"
        self.setting={
            "USERSELFTEAMCHANGE":False
        }

    def join(self, userobj):
        super().join(userobj)
        name=userobj.name
        for user in self.userlist.values():
            user.send({"com":"userjoin","mod":self.PAGENAME,"user":name,"auth":self.AuthSetTeam(user,name)})
    
    def leave(self, userobj):
        super().leave(userobj)
        if userobj.name in self.userteams:
            self.userteams.pop(userobj.name)

    def canSetTeam(self,userobj,name):
        if self.running:
            return False
        return self.AuthSetTeam(userobj,name)

    def AuthSetTeam(self,userobj,name):
        auth=self.userauths[userobj.name]
        if auth<1:
            return False
        if userobj.name!=name and auth==1:
            return False
        if auth==1 and not self.setting["USERSELFTEAMCHANGE"]:
            return False
        return True

    def startGame(self,data):
        sizedata=data["dim"]
        teamcount=data["numteams"]
        board=data["boarddata"]
        self.order=data["turnorder"]
        self.logic=Chess.Logic.Logic.genboard(teamcount,sizedata,board)
        self.turnorder=Chess.turngen(data["turnorder"])
        self.turn=next(self.turnorder)
        self.logic.teamturn=self.turn
        self.running=True
        c={"com":"loadboard","data":self.exportBoard()}
        self.broadcast(c)
        self.logic.updateallmoves()
    
    def stopGame(self):
        self.running=False
        del self.turnorder
        del self.logic
        del self.order
        com={"com":"loadboard","data":self.exportBoard()}
        self.broadcast(com)
    
    def AuthMove(self, userobj, pos):
        p=self.logic.getpiece(pos=pos)
        if userobj.name not in self.userteams:
            return False
        if p.team != self.userteams[userobj.name]:
            return False
        return True

    def makeMove(self, userobj, pos1,pos2):
        if not self.running:
            return
        if not self.logic.ispiece(pos=pos1):
            return
        if not self.AuthMove(userobj,pos1):
            return
        if not self.logic.canmove(pos1,pos2):
            return
        r=self.logic.reqmovepiece(pos1,pos2)
        if not r:
            return
        self.broadcast({"com":"loadmoves","dif":r})
        self.endturn()
        return True

    def endturn(self):
        self.turn=next(self.turnorder)
        self.logic.teamturn=self.turn
        self.logic.updateallmoves()


    def handlecommand(self,usr,com:dict):
        match com:
            case {"com":"togglegamerun",**_u}:
                if self.userauths[usr.name]<3:
                    c={"com":"setauth","action":"gametoggle","mod":self.PAGENAME,"auth":False}
                    usr.send(c)
                    return
                if self.running:
                    self.stopGame()
                else:
                    d=Chess.Stateloader.getBoard(self.boardname)
                    self.startGame(d)
            case {"com":"getauth","action":"gametoggle",**_u}:
                c={"com":"setauth","action":"gametoggle","mod":self.PAGENAME,"auth":self.userauths[usr.name]>=3}
                usr.send(c)
            case {"com":"getboard",**_u}:
                r=self.exportBoard()
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
                if not self.makeMove(usr,pos1,pos2):
                    usr.send({"com":"returnpiece","pos":pos1.intcoords(),"mod":self.PAGENAME})
            case {"com":"getmoves","piecepos":pos,**_u} if self.running:
                vpos=vector.fromtuple(pos)
                r=self.getpossiblemoves(vpos)
                c={"com":"displaymoves","mod":self.PAGENAME,"moves":r,"pos":pos}
                usr.send(c)

    def getpossiblemoves(self,pos):
        if not self.running:
            return
        p=self.logic.getpiece(pos=pos)
        if not p:
            return
        return [m.intcoords() for m in p.getallmoves()]

    def setTeam(self,usr,name,team):
        if not self.canSetTeam(usr,name):
            return
        self.userteams[name]=team
        self.broadcast({"com":"teamchanged","name":name,"team":team,"mod":self.PAGENAME})

    def exportBoard(self,):
        if not self.running:
            d=Chess.Stateloader.getBoard(self.boardname)
            d["running"]=self.running
            return d
        d=self.logic.data
        dup=[]
        for x,strip in enumerate(d):
            dup.append([])
            for y,p in enumerate(strip):
                if isinstance(p,Chess.Logic.Piece):
                    p=p.export()
                dup[x].append(p)
        bd={
            "numteams":len(self.logic.teams),
            "dim":[self.logic.WIDTH,self.logic.HEIGHT],
            "turnorder":self.order,
            "running":self.running,
            "boarddata":dup
        }
        return bd
    
    def exportUserData(self,userobj):
        d=[]
        for n in self.userlist.keys():
            if n not in self.userteams:
                d.append((n,self.AuthSetTeam(userobj,n),None))
            else:
                d.append((n,self.AuthSetTeam(userobj,n),self.userteams[n]))
        return d
        

class RoomServer:
    def __init__(self) -> None:
        self.roomindex:dict[str,Room]={}
        self.userindex={}
        self.mainRoom=SelRoom("mainroom")
        self.roomindex["menu"]=self.mainRoom

    def createRoom(self, roomcls, Id, **kwargs) -> Room:
        if not isinstance(roomcls,type(Room)):
            raise TypeError("Cannot be instance")
        if not issubclass(roomcls,Room):
            raise TypeError("Room classes must inherit room")
        if Id not in self.roomindex:
            r:Room=roomcls(Id, **kwargs)
            self.roomindex[Id]=r
            if r.AuthSee():
                self.mainRoom.broadcast({"com":"showroom","name":Id,"password":bool(r.password),"private":r.private})
            return r
        else:
            raise FileExistsError

    def joinRoom(self,userobj,roomId:str,password=None):
        if roomId not in self.roomindex:
            raise FileNotFoundError
        if userobj.name in self.userindex:
            self.leaveRoom(userobj)
        room=self.roomindex[roomId]
        if room.AuthJoin(password):
            self.userindex[userobj.name]=roomId
            self.roomindex[roomId].join(userobj)
        else:
            raise EnvironmentError


    
    def inRoom(self,userobj):
        if userobj.name not in self.userindex:
            return False
        if not self.userindex[userobj.name]:
            return False
        return True

    def leaveRoom(self,userobj):
        if not self.inRoom(userobj):
            return
        roomId=self.userindex[userobj.name]
        self.userindex.pop(userobj.name)
        if roomId not in self.roomindex:
            return
        self.roomindex[roomId].leave(userobj)
        if not self.roomindex[roomId].canPersist():
            self.destroy(roomId)
    
    def broacast(self,roomId,com,user=None):
        if not (isinstance(user,(str)) or not user):
            user=user.name
        if roomId not in self.roomindex:
            return
        self.roomindex[roomId].broadcast(com,user)
    
    def destroy(self,roomId):
        room=self.roomindex[roomId]
        room.close()
        for user in list(room.userlist.values()):
            self.leaveRoom(user)
        if room.AuthSee():
            com={"com":"hideroom","name":roomId,"mod":self.mainRoom.PAGENAME}
            self.mainRoom.broadcast(com)
        self.roomindex.pop(roomId)
        del room

    def send(self,roomId,com,user):
        if roomId not in self.roomindex:
            return
        self.roomindex[roomId].send(com,user.name)

    def usercommands(self,user,com):
        if user.auth<0:
            logging.warn(f"Unauthorised {user} attempted to access rooms")
            return
        match com:
            case {"forwardtoroom":True,"com":_,**_u}:
                if user.name not in self.userindex:
                    user.clientError("NotInRoom","stateHandler")
                if not self.userindex[user.name]:
                    user.clientError("NotInRoom","stateHandler")
                self.roomindex[self.userindex[user.name]].handlecommand(user,com)
            case {"com":"listenroomevent",**_u}:
                if self.inRoom(user):
                    return
                self.joinRoom(user,"menu")
            case {"com":"createroom","roomname":roomname,"roompass":roompass,"private":private,**_u}:
                try:
                    r:ChessRoom=self.createRoom(ChessRoom,roomname,password=roompass,private=private)
                    r.setAuth(user,3)
                    self.joinRoom(user,roomname,roompass)
                    user.send({"com":"joinroom","mod":"stateHandler","type":self.roomindex[roomname].PAGENAME})
                except FileExistsError:
                    user.clientError("RoomExists",self.mainRoom.PAGENAME)
            case {"com":"joinroom","roomname":roomname,"roompass":roompass,**_u}:
                roomname=com["roomname"]
                roompass=com["roompass"]
                try:
                    self.joinRoom(user,roomname,roompass)
                    user.send({"com":"joinroom","mod":"stateHandler","type":self.roomindex[roomname].PAGENAME})
                except (EnvironmentError, FileNotFoundError, FileExistsError):
                    user.clientError("AuthDeny",self.mainRoom.PAGENAME)
            case {"com":"leaveroom",**_u}:
                self.leaveRoom(user)
                self.joinRoom(user,"menu")
            case {"com":"getrooms",**_u}:
                if not self.inRoom(user):
                    self.joinRoom(user,"menu")
                visiblerooms=[
                {"name":room.name,"password":bool(room.password)}
                for room in self.roomindex.values() if room.AuthSee()
                ]
                com={"com":"refreshrooms","roomarray":visiblerooms,"mod":self.mainRoom.PAGENAME}
                user.send(com)
