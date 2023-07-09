from .Logic import Piece
from ..vectormath import *



class Pawn(Piece):
    name="pawn"
    def __init__(self,logic, x=0, y=0,direction=None,team=0,**kwargs) -> None:
        if not direction:
            if team==1:
                direction=2
            else:
                direction=0
        else:
            direction%=4
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
            if not self.logic.validatebounds(move.x,move.y):
                break
            if move.intcoords() in boarddata:
                break
            availmoves.append(move)
        for take in self.takes:
            take+=self.position
            if not self.logic.validatebounds(take.x,take.y):
                continue
            if take.intcoords() not in boarddata:
                continue
            if boarddata[take.intcoords()].team==self.team:
                continue
            availtakes.append(take)
        return super().validatecheck(availmoves,availtakes,cc)
    
    def export(self):
        e=super().export()
        e.update(direction=self.direction)
        return e

    def move(self,move,data):
        super().move(move,data)
        if len(self.startmove)!=0:
            self.startmove=()
        m=move+self.moves[0]
        x=m.x
        y=m.y
        if self.logic.validatebounds(x,y):
            return
        self.promote()
        
    def promote(self):
        x, y = self.position.intcoords()
        self.logic.addpiece(x,y,"queen",self.team)
class CowardPawn(Pawn):
    name="pawn"
    #an inside joke that the pawn instead of promoting would just turn around
    def promote(self):
        x, y = self.position.intcoords()
        self.logic.addpiece(x,y,"cpawn",self.team,direction=self.direction+2)   
class Rook(Piece):
    name="rook"
    def __init__(self, logic, x=0, y=0, team=0,**kwargs) -> None:
        self.lines:list[vector]=vector(0,1).all90()
        super().__init__(logic, x, y, team)
    def getavailmoves(self,boarddata,cc=False):
        availmoves=[]
        availtakes=[]
        for direction in self.lines:
            searchpos=self.position
            while True:
                searchpos+=direction
                if not self.logic.validatebounds(searchpos.x,searchpos.y):
                    break
                if searchpos.intcoords() in boarddata:
                    if boarddata[searchpos.intcoords()].team != self.team:
                        availtakes.append(searchpos)
                    break
                availmoves.append(searchpos)
        return super().validatecheck(availmoves,availtakes,cc)

class King(Piece):
    name="king"
    def __init__(self,logic,x=0, y=0,team=0,**kwargs) -> None:
        self.moves=vector(0,1).all90()+vector(1,1).all90()
        logic.teams[team].kings.append(self)
        super().__init__(logic, x, y,team)
    def getavailmoves(self,boarddata,cc=False):
        availmoves=[]
        availtakes=[] 
        for move in self.moves:
            move+=self.position
            if not self.logic.validatebounds(move.x,move.y):
                continue
            if move.intcoords() in boarddata:
                if boarddata[move.intcoords()].team==self.team:
                    continue
                availtakes.append(move)
            else:
                availmoves.append(move)
        return super().validatecheck(availmoves,availtakes,cc)
    def checkcheck(self,moves):
        data=self.logic.makecopy()
        x=int(self.position.x)
        y=int(self.position.y)
        data.pop(self.position.intcoords())
        safemoves=[]
        for move in moves:
            if move.intcoords() in data:
                takenpiece=data[move.intcoords()]
            else:
                takenpiece=None
            data[move.intcoords()]=self
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
            if takenpiece:
                data[move.intcoords()]=takenpiece
            else:
                data.pop(move.intcoords())
        return safemoves

class Bishop(Piece):
    name="bishop"
    def __init__(self, logic, x=0, y=0, team=0,**kwargs) -> None:
        self.lines=vector(1,1).all90()
        super().__init__(logic, x, y, team)
    def getavailmoves(self,boarddata,cc=False):
        availmoves=[]
        availtakes=[]
        for direction in self.lines:
            searchpos=self.position
            while True:
                searchpos+=direction
                if not self.logic.validatebounds(searchpos.x,searchpos.y):
                    break
                if searchpos.intcoords() in boarddata:
                    if boarddata[searchpos.intcoords()].team != self.team:
                        availtakes.append(searchpos)
                    break
                availmoves.append(searchpos)
        return super().validatecheck(availmoves,availtakes,cc)

class Queen(Piece):
    name="queen"
    def __init__(self, logic, x=0, y=0, team=0,**kwargs) -> None:
        self.lines=vector(1,1).all90()+vector(0,1).all90()
        super().__init__(logic, x, y, team)
    def getavailmoves(self,boarddata,cc=False):
        availmoves=[]
        availtakes=[]
        for direction in self.lines:
            searchpos=self.position
            while True:
                searchpos+=direction
                if not self.logic.validatebounds(searchpos.x,searchpos.y):
                    break
                if searchpos.intcoords() in boarddata:
                    if boarddata[searchpos.intcoords()].team != self.team:
                        availtakes.append(searchpos)
                    break
                availmoves.append(searchpos)
        return super().validatecheck(availmoves,availtakes,cc)

class Knight(Piece):
    name="knight"
    def __init__(self, logic, x=0, y=0, team=0,**kwargs) -> None:
        self.moves=vector(1,2).all90()+vector(-1,2).all90()
        super().__init__(logic, x, y, team)
    def getavailmoves(self,boarddata,cc=False):
        availmoves=[]
        availtakes=[]
        for move in self.moves:
            move+=self.position
            if not self.logic.validatebounds(move.x,move.y):
                continue
            if move.intcoords() in boarddata:
                if boarddata[move.intcoords()].team==self.team:
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