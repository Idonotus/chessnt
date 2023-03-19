from .Piece import Piece
from ..vectormath import *



class Pawn(Piece):
    def __init__(self,logic, x=0, y=0,direction=None,team=0) -> None:
        if not direction:
            if team==1:
                direction=2
            else:
                direction=0
        self.moves=(vector(0,1).rot90(direction),)
        self.takes=(vector(1,1).rot90(direction),vector(-1,1).rot90(direction))
        self.startmove=(vector(0,2).rot90(direction),)
        self.direction=direction
        super().__init__(logic, x, y,team)
    def getavailmoves(self,boarddata,cc=False):
        availmoves=[]
        availtakes=[] 
        for move in self.moves+self.startmove:
            move+=self.position
            if not self.logic.validatemove(move.x,move.y):
                break
            if boarddata[int(move.x)][int(move.y)]:
                break
            availmoves.append(move)
        for take in self.takes:
            take+=self.position
            if not self.logic.validatemove(take.x,take.y):
                continue
            if not boarddata[int(take.x)][int(take.y)]:
                continue
            if boarddata[int(take.x)][int(take.y)].team==self.team:
                continue
            availtakes.append(take)
        return super().validatecheck(availmoves,availtakes,cc)
    def move(self,move,data):
        
        a=super().move(move,data)
        if a=="return":
            return a
        if len(self.startmove)!=0:
            self.startmove=()
        m=move+self.moves[0]
        x=m.x
        y=m.y
        if self.logic.validatemove(x,y):
            return a
        a=[a,"promote"]
        self.logic.addpiece(int(move.x),int(move.y),"queen",self.team)
        return a
class CowardPawn(Pawn):
    def move(self,move,data):
        a=super().move(move,data)
        if a=="return":
            return a
        if len(self.startmove)!=0:
            self.startmove=()
        m=move+self.moves[0]
        x=m.x
        y=m.y
        if self.logic.validatemove(x,y):
            return a
        self.logic.addpiece(int(move.x),int(move.y),"cpawn",self.team,direction=self.direction+2)
        return a        
class Rook(Piece):
    def __init__(self, logic, x=0, y=0, team=0) -> None:
        self.lines=vector(0,1).all90()
        super().__init__(logic, x, y, team)
    def getavailmoves(self,boarddata,cc=False):
        availmoves=[]
        availtakes=[]
        for direction in self.lines:
            searchpos=self.position
            while True:
                searchpos+=direction
                if not self.logic.validatemove(searchpos.x,searchpos.y):
                    break
                if boarddata[int(searchpos.x)][int(searchpos.y)]:
                    if boarddata[int(searchpos.x)][int(searchpos.y)].team!=self.team:
                        availtakes.append(searchpos)
                    break
                availmoves.append(searchpos)
        return super().validatecheck(availmoves,availtakes,cc)

class King(Piece):
    def __init__(self,logic,x=0, y=0,team=0) -> None:
        self.moves=vector(0,1).all90()+vector(1,1).all90()
        logic.teams[team].kings.append(self)
        super().__init__(logic, x, y,team)
    def getavailmoves(self,boarddata,cc=False):
        availmoves=[]
        availtakes=[] 
        for move in self.moves:
            move+=self.position
            if not self.logic.validatemove(move.x,move.y):
                continue
            if boarddata[int(move.x)][int(move.y)]:
                if boarddata[int(move.x)][int(move.y)].team==self.team:
                    continue
                availtakes.append(move)
            else:
                availmoves.append(move)
        return super().validatecheck(availmoves,availtakes,cc)
    def checkcheck(self,moves):
        data=self.logic.makecopy()
        x=int(self.position.x)
        y=int(self.position.y)
        data[x][y]=None
        safemoves=[]
        for move in moves:
            takenpiece=data[int(move.x)][int(move.y)]
            data[int(move.x)][int(move.y)]=self
            possiblemoves=self.logic.getallmoves(data,teams=[self.team],teaminv=True)[2]
            unsafe=False
            for king in self.logic.teams[self.team].kings:
                if king is self:
                    if move in possiblemoves:
                        unsafe=True
                        break
                elif king.position in possiblemoves:
                    unsafe=True
                    break
            if not unsafe:
                safemoves.append(move)
            data[int(move.x)][int(move.y)]=takenpiece
        return safemoves

class Bishop(Piece):
    def __init__(self, logic, x=0, y=0, team=0) -> None:
        self.lines=vector(1,1).all90()
        super().__init__(logic, x, y, team)
    def getavailmoves(self,boarddata,cc=False):
        availmoves=[]
        availtakes=[]
        for direction in self.lines:
            searchpos=self.position
            while True:
                searchpos+=direction
                if not self.logic.validatemove(searchpos.x,searchpos.y):
                    break
                if boarddata[int(searchpos.x)][int(searchpos.y)]:
                    if boarddata[int(searchpos.x)][int(searchpos.y)].team!=self.team:
                        availtakes.append(searchpos)
                    break
                availmoves.append(searchpos)
        return super().validatecheck(availmoves,availtakes,cc)

class Queen(Piece):
    def __init__(self, logic, x=0, y=0, team=0) -> None:
        self.lines=vector(1,1).all90()+vector(0,1).all90()
        super().__init__(logic, x, y, team)
    def getavailmoves(self,boarddata,cc=False):
        availmoves=[]
        availtakes=[]
        for direction in self.lines:
            searchpos=self.position
            while True:
                searchpos+=direction
                if not self.logic.validatemove(searchpos.x,searchpos.y):
                    break
                if boarddata[int(searchpos.x)][int(searchpos.y)]:
                    if boarddata[int(searchpos.x)][int(searchpos.y)].team!=self.team:
                        availtakes.append(searchpos)
                    break
                availmoves.append(searchpos)
        return super().validatecheck(availmoves,availtakes,cc)

class Knight(Piece):
    def __init__(self, logic, x=0, y=0, team=0) -> None:
        self.moves=vector(1,2).all90()+vector(-1,2).all90()
        super().__init__(logic, x, y, team)
    def getavailmoves(self,boarddata,cc=False):
        availmoves=[]
        availtakes=[]
        for move in self.moves:
            move+=self.position
            if not self.logic.validatemove(move.x,move.y):
                continue
            if boarddata[int(move.x)][int(move.y)]:
                if boarddata[int(move.x)][int(move.y)].team==self.team:
                    continue
                availtakes.append(move)
                continue
            availmoves.append(move)
        return super().validatecheck(availmoves,availtakes,cc)
def getallpieces():
    return {
        "cpawn":CowardPawn,
        "king":King,
        "queen":Queen,
        "pawn":Pawn,
        "rook":Rook,
        "bishop":Bishop,
        "knight":Knight
    }