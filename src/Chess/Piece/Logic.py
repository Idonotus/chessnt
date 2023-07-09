from ..vectormath import *
import logging
from typing import Iterable

class Piece:
    name="piece"
    def __init__(self,logic,x=0,y=0,team=0,**kwargs):
        self.inactive=False
        self.logic=logic
        self.position:vector=vector(x,y)
        self.availmoves:list[vector]=[]
        self.availtakes:list[vector]=[]
        self.team=team
    
    def setinactive(self,*args):
        self.inactive=True
    
    def setactive(self,*args):
        self.inactive=False

    def getallmoves(self):
        return self.availmoves+self.availtakes

    def export(self):
        return {"name":self.name,"pos":self.position.intcoords(),"team":self.team,"inactive":self.inactive}

    def move(self,move,data):
        if move not in self.availmoves and move not in self.availtakes:
            return
        pos=self.position.intcoords()
        pos2=move.intcoords()
        data.pop(pos)
        data[pos2]=self
        self.position=move

    def canmove(self,move):
        return move in self.availmoves or move in self.availtakes
    
    def erasemoves(self):
        self.availmoves=[]
        self.availtakes=[]

    def updateMoves(self,boarddata,cc):
        self.erasemoves()
        self.availmoves,self.availtakes=self.getavailmoves(boarddata,cc)

    def validatecheck(self,availmoves,availtakes,cc=False):
        if cc:
            availmoves=self.checkcheck(availmoves)
            availtakes=self.checkcheck(availtakes)
        return availmoves,availtakes

    def getavailmoves(self,*args,**kwargs):
        logging.error("Class has not overwritten getmoves functionality")

    def checkcheck(self,moves:Iterable[vector]):
        data=self.logic.makecopy()
        data.pop(self.position.intcoords())
        safemoves=[]
        for move in moves:
            if move.intcoords()in data:
                takenpiece=data[move.intcoords()]
            else:
                takenpiece=None
            data[move.intcoords()]=self
            possiblemoves=self.logic.getallmoves(data,teams=[self.team],teaminv=True)[1]
            unsafe=False
            for king in self.logic.teams[self.team].kings:
                if king.position in possiblemoves:
                    unsafe=True
                    break
            if not unsafe:
                safemoves.append(move)
            if takenpiece:
                data[move.intcoords()]=takenpiece
            else:
                data.pop(move.intcoords())
        return safemoves

    def __eq__(self, __value) -> bool:
        if not isinstance(__value,type(self)):
            return False
        return (self.position,self.team,self.inactive)==(__value.position,__value.team,__value.inactive)