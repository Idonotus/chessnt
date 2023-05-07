from . import PieceLogic
import logging
class Team:
    """Container for team data"""
    kings=[]
    checked=False
        
class Logic:
    """Handles chess logic. Essential for chess to actually work"""
    def __init__(self,width,height,numteams,game) -> None:
        self.WIDTH=width
        self.HEIGHT=height
        self.data=[]
        self.teams=[]
        self.teamturn=[1]
        for i in range(numteams):
            self.teams.append(Team)
        for x in range(width):
            self.data.append([])
            for _ in range(height):
                self.data[x].append(None)
        self.PIECES=PieceLogic.getallpieces()
        self.game=game
    
    def endcheck(self):
        turntemp=self.teamturn
        self.teamturn=list(range(len(self.teams)))
        for i,_ in enumerate(self.teams):
            if hasattr(self.teams[i],"non-player"):
                continue
            teammoves=self.getallmoves(teams=[i],cc=True)[2]
            if len(teammoves)==0:
                if self.game!=None:
                    self.game.teamlose(i)
        self.teamturn=turntemp
    
    def incheckcheck(self,team):
        kings=self.teams[team]
        takes=self.getallmoves(teams=[team],teaminv=True)[2]
        for king in kings:
            if king.position in takes:
                if self.game!=None:
                    self.game.incheck(team,king.position)

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
        for ystrip in data:
            for tile in ystrip:
                if not tile:
                    continue
                tile.updateMoves(data,cc=True)

    def getallmoves(self,data=None,teams=[],teaminv=False,cc=False):
        if not data:
            data=self.data
        takes=[]
        moves=[]
        for ystrip in data:
            for tile in ystrip:
                if not tile:
                    continue
                if not(teaminv ^ (tile.team in teams)):
                    continue
                temp = tile.getavailmoves(data,cc)
                moves+=temp[0]
                takes+=temp[1]
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
        if team is not None and team not in self.teamturn:
                return False
        print("a")
        movepiece=self.getpiece(pos=pos1)
        if not movepiece:
            return False
        print("b")
        if movepiece.team!=team:
            return False
        print("c")
        return movepiece.canmove(pos2)

    def movepiece(self,pos1,pos2):
        p=self.getpiece(pos=pos1)
        if not p:
            return False
        if not self.canmove(pos1,pos2,p.team):
            return False
        c=self.makecopy()
        a=p.move(pos2,self.data)
        if a=="return":
            return False
        return self.getdifferences(c,self.data)
        

    def getpiece(self,*, pos=None, x=None, y=None):
        if pos:
            return self.data[int(pos.x)][int(pos.y)]
        if not (x is None and y is None):
            return self.data[x][y]