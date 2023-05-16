from .Logic import PieceLogic
import logging
class Team:
    """Container for team data"""
    def __init__(self) -> None:
        self.kings=[]
        self.checked=False
        
class Logic:
    """Handles chess logic. Essential for chess to actually work"""
    def __init__(self,width,height,numteams,game) -> None:
        self.WIDTH=width
        self.HEIGHT=height
        self.data=[]
        self.teams=[]
        self.inactiveteams=[]
        self.teamturn=[1]
        for i in range(numteams):
            self.teams.append(Team())
        for x in range(width):
            self.data.append([])
            for _ in range(height):
                self.data[x].append(None)
        self.PIECES=PieceLogic.getallpieces()
        self.game=game

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
        p=self.getpieces(teams=[teamid],inactive=False)
        for t in p:
            t.updateMoves()
            t.inactive=False

    def getpieces(self,data=None,teams=[],teaminv=False,inactive=True):
        if not data:
            data=self.data
        pieces=[]
        for ystrip in data:
            for tile in ystrip:
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
        for i,_ in enumerate(self.teams):
            if hasattr(self.teams[i],"non-player"):
                continue
            teammoves=self.getallmoves(teams=[i],cc=True)[2]
            if len(teammoves)==0:
                if self.game!=None:
                    self.game.teamlose(i)
    
    def matecheck(self,team):
        return len(self.getallmoves(teams=[team]))>0

    def makecopy(self):
        copy=[]
        for n,ystrip in enumerate(self.data):
            copy.append([])
            for tile in ystrip:
                copy[n].append(tile)
        return copy

    def validatemove(self,x,y):
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

    def genboard():
        pass

    def addpiece(self,x,y,name,team,**kwargs):
        name=name.lower()
        if name not in self.PIECES:
            logging.warn(f"Logic not found for piece \"{name}\". Using dummy instead")
            name="dummy"
        if not 0<=x<len(self.data):
            logging.warn("Out of bounds")
        if not 0<=y<len(self.data[x]):
            logging.warn("Out of bounds")
        self.data[x][y]=self.PIECES[name](logic=self,x=x,y=y,team=team,**kwargs)

    def getdifferences(self,base:list,changed:list):
        diff=[((x,y),changed[x][y]) for x in range(len(changed)) for y in range(len(changed[x])) if changed[x][y]!=base[x][y]]
        return diff

    def canmove(self,pos1,pos2,team=None):
        if not self.validatemove(pos2.x,pos2.y):
            return False
        if team is not None and team not in self.teamturn:
                return False
        movepiece=self.getpiece(pos=pos1)
        if not movepiece:
            return False
        if movepiece.team!=team and team is not None:
            return False
        return movepiece.canmove(pos2)

    def movepiece(self,pos1,pos2):
        p=self.getpiece(pos=pos1)
        if not p:
            return
        c=self.makecopy()
        a=p.move(pos2,self.data)
        if a=="return":
            return
        return self.getdifferences(c,self.data)
        
    def ispiece(self,*, pos=None, x=None, y=None):
        return bool(self.getpiece(pos=pos,x=x,y=y))

    def getpiece(self,*, pos=None, x=None, y=None):
        if pos:
            return self.data[int(pos.x)][int(pos.y)]
        if not (x is None and y is None):
            return self.data[x][y]