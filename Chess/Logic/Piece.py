from ..vectormath import *
class Piece():
    def __init__(self,logic,x=0,y=0,team=0):
        self.logic=logic
        self.position=vector(x,y)
        self.availmoves=[]
        self.availtakes=[]
        self.team=team
        
    def checkmove(self,move):
        if move==self.position:
            return "return"
        if move in self.availtakes:
            return "take"
        if move in self.availmoves:
            return "move"
        return "return"
        

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
        if self.team in self.logic.teamturn:
            self.availmoves,self.availtakes=self.getavailmoves(boarddata,cc)

    def validatecheck(self,availmoves,availtakes,cc=False):
        if cc:
            availmoves=self.checkcheck(availmoves)
            availtakes=self.checkcheck(availtakes)
        return availmoves,availtakes

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
