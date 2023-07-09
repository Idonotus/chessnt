from __future__ import annotations
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

class Logic:
    """Handles chess logic. Essential for chess to actually work"""
    def __init__(self,width,height,numteams) -> None:
        self.WIDTH=width
        self.HEIGHT=height
        self.data:dict[tuple,Piece]={}
        self.teams:dict[int,Team]={}
        self.inactiveteams={}
        self.teamturn:Turn=Turn(1)
        for i in range(numteams):
            self.teams[i]=Team()
        self.PIECES=PieceLogic.getallpieces()
    
    def setinactive(self,teamid):
        if teamid in self.inactiveteams:
            return
        self.inactiveteams[teamid]=self.teams[teamid]
        p=self.getpieces(teams=[teamid],inactive=False)
        for t in p:
            t.setinactive(teamid)

    def setactive(self,teamid):
        if teamid not in self.inactiveteams:
            return
        self.inactiveteams.pop(teamid)
        p=self.getpieces(teams=[teamid],inactive=True)
        for t in p:
            t.setactive(teamid)

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

    def kingsalive(self,teamid):
        t=self.teams[teamid]
        if hasattr(t,"non_player"):
            if t.non_player:
                return True
        for k in t.kings:
            k:PieceLogic.King
            if k!=self.getpiece(pos=k.position):
                return False
        return True

    def incheckmate(self,teamid):
        t=self.teams[teamid]
        if hasattr(t,"non_player"):
            if t.non_player:
                return False
        teammoves=self.getallmoves(teams=[teamid],cc=True)[2]
        if len(teammoves)==0:
            return True
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
    def genboard(numteams,dim,boarddata)->Logic:
        l=Logic(dim[0],dim[1],numteams)
        if isinstance(boarddata,dict):
            for pos,tile in boarddata.items():
                l.addpiece(x=pos[0],y=pos[1],**tile)
        if isinstance(boarddata,list):
            for ystrip in boarddata:
                for tile in ystrip:
                    if not tile:
                        continue
                    tile=tile.copy()
                    x, y=tile.pop("pos")
                    l.addpiece(x=x,y=y,**tile)
        return l
