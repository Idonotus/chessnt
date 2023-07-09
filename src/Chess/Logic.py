from .Piece import PieceLogic
from .Piece.Logic import Piece
from .vectormath import vector
from .Turns import Turn
import logging
from typing import overload
class Team:
    """Container for team data"""
    def __init__(self) -> None:
        self.kings=[]
        self.checked=False

class Logic:
    """Handles chess logic. Essential for chess to actually work"""
    def __init__(self,width,height,numteams) -> None:
        self.WIDTH=width
        self.HEIGHT=height
        self.data={}
        self.teams=[]
        self.inactiveteams=[]
        self.teamturn:Turn=Turn(1)
        for i in range(numteams):
            self.teams.append(Team())
        self.PIECES=PieceLogic.getallpieces()
    
    def setinactive(self,teamid):
        if teamid in self.inactiveteams:
            return
        self.inactiveteams.append(teamid)
        p=self.getpieces(teams=[teamid],inactive=False)
        for t in p:
            t.erasemoves()
            t.inactive=True

    def setactive(self,teamid):
        if teamid not in self.inactiveteams:
            return
        self.inactiveteams.remove(teamid)
        p=self.getpieces(teams=[teamid],inactive=True)
        for t in p:
            t.inactive=False
            t.updateMoves()

    def getpieces(self,data=None,teams=[],teaminv=False,inactive=True) -> list[Piece]:
        if not data:
            data=self.data
        pieces=[]
        for pos in data:
            tile=data[pos]
            if not tile:
                continue
            if not(teaminv ^ (tile.team in teams)):
                continue
            if inactive and hasattr(tile,"inactive"):
                if tile.inactive:
                    continue
            pieces.append(tile)
        return pieces

    def endcheck(self):
        for i,t in enumerate(self.teams):
            if hasattr(t,"non-player"):
                continue
            teammoves=self.getallmoves(teams=[i],cc=True)[2]
            if len(teammoves)==0:
                return i+1
        return False
    
    def matecheck(self,team):
        return len(self.getallmoves(teams=[team]))>0

    def makecopy(self):
        copy=self.data.copy()
        return copy

    def validatebounds(self,x,y):
        if not 0<=x<self.WIDTH:
            return False
        if not 0<=y<self.HEIGHT:
            return False
        return True

    def updateallmoves(self,data=None):
        if not data:
            data=self.data
        p=self.getpieces(data,teaminv=True)
        for tile in p:
            tile.updateMoves(data,cc=True)

    def getallmoves(self,data=None,teams=[],teaminv=False,cc=False):
        if not data:
            data=self.data
        p=self.getpieces(data,teams,teaminv)
        takes=[]
        moves=[]
        for piece in p:
            a,b=piece.getavailmoves(data,cc)
            moves+=a
            takes+=b
        actions=moves+takes
        return moves,takes,actions

    def addpiece(self,x,y,name,team,**kwargs):
        name=name.lower()
        if name not in self.PIECES:
            logging.warn(f"Logic not found for piece \"{name}\". Using dummy instead")
            name="dummy"
        if not self.validatebounds(x,y):
            logging.warn("Out of bounds")
        self.data[(x,y)]=self.PIECES[name](logic=self,x=x,y=y,team=team,**kwargs)

    def getdifferences(self,base:dict,changed:dict):
        diff=[]
        allpos=set(base.keys())
        allpos.update(changed.keys())
        for pos in allpos:
            if not ((pos in base) ^ (pos in changed)):
                if base[pos]==changed[pos]:
                    continue
                else:
                    dif_pair=[pos,changed[pos]]
            elif pos in changed:
                dif_pair=[pos,changed[pos]]
            else:
                dif_pair=[pos,None]
            if isinstance(dif_pair[1],Piece):
                dif_pair[1]=dif_pair[1].export()
            diff.append(dif_pair)
        return diff

    def canmove(self,pos1,pos2,team=False):
        if not self.validatebounds(pos2.x,pos2.y):
            return False
        movepiece=self.getpiece(pos=pos1)
        if not movepiece:
            return False
        if team and not self.teamturn.validatemove(movepiece):
            return False
        return movepiece.canmove(pos2)

    def reqmovepiece(self,pos1,pos2):
        p=self.getpiece(pos=pos1)
        if not p:
            return
        c=self.makecopy()
        a=p.move(pos2,self.data)
        if a=="return":
            return
        return self.getdifferences(c,self.data)
    
    @overload
    def ispiece(self,*, pos:vector=None) -> bool:...
    @overload
    def ispiece(self,*, x:int=None, y:int=None) -> bool:...
    def ispiece(self,*, pos:vector=None, x:int=None, y:int=None) -> bool:
        if not (x is None and y is None) and pos is None:
            pos=vector(x,y)
        return pos.intcoords() in self.data
    
    @overload
    def getpiece(self,*, x:int=None, y:int=None) -> Piece:...
    @overload
    def getpiece(self,*, pos:vector=None) -> Piece:...
    def getpiece(self,*, pos:vector=None, x:int=None, y:int=None) -> Piece:
        if not (x is None and y is None) and pos is None:
            pos=vector(x,y)
        if isinstance(pos,vector):
            return self.data[pos.intcoords()]
        
    @staticmethod
    def genboard(numteams,dim,boarddata):
        l=Logic(dim[0],dim[1],numteams)
        for ystrip in boarddata:
            for tile in ystrip:
                if not tile:
                    continue
                tile=tile.copy()
                x, y=tile.pop("pos")
                l.addpiece(x=x,y=y,**tile)
        return l
