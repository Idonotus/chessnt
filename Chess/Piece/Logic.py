from ..vectormath import *
import logging

class Piece:
    name="piece"
    def __init__(self,logic,x=0,y=0,team=0):
        self.inactive=False
        self.logic=logic
        self.position=vector(x,y)
        self.availmoves=[]
        self.availtakes=[]
        self.team=team
    
    def getallmoves(self):
        return self.availmoves+self.availtakes

    def export(self):
        return {"name":self.name,"pos":self.position.intcoords(),"team":self.team}

    def move(self,move,data):
        if move not in self.availmoves and move not in self.availtakes:
            return
        x, y=self.position.intcoords()
        mx, my=move.intcoords()
        data[x][y]=None
        data[mx][my]=self
        self.position=move

    def canmove(self,move):
        return move in self.availmoves or move in self.availtakes

    def takepiece(self,x,y):
        self.board.data[x][y].delete()
        self.movepiece(x,y)

    def movepiece(self,x,y):
        pos=self.position
        self.boarddata[x][y]=self
        self.position=vector(x,y)
        self.boarddata[int(pos.x)][int(pos.y)]=None
    
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

    def checkcheck(self,moves):
        data=self.logic.makecopy()
        x=int(self.position.x)
        y=int(self.position.y)
        data[x][y]=None
        safemoves=[]
        for move in moves:
            takenpiece=data[int(move.x)][int(move.y)]
            data[int(move.x)][int(move.y)]=self
            possiblemoves=self.logic.getallmoves(data,teams=[self.team],teaminv=True)[1]
            unsafe=False
            for king in self.logic.teams[self.team].kings:
                if king.position in possiblemoves:
                    unsafe=True
                    break
            if not unsafe:
                safemoves.append(move)
            data[int(move.x)][int(move.y)]=takenpiece
        return safemoves

    def __eq__(self, __value) -> bool:
        if not isinstance(__value,type(self)):
            return False
        return (self.position,self.team)==(__value.position,__value.team)