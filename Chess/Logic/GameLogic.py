from . import PieceLogic
import warnings
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
        self.pieceauth=[0,1]
        self.teamturn=[0]
        for i in range(numteams):
            self.teams.append(Team)
        for x in range(width):
            self.data.append([])
            for _ in range(height):
                self.data[x].append(None)
        self.PIECES=PieceLogic.getallpieces()
        self.game=game
    
    def endcheck(self):
        authtemp=self.pieceauth
        turntemp=self.teamturn
        self.teamturn=list(range(len(self.teams)))
        self.pieceauth=self.teamturn
        for i,_ in enumerate(self.teams):
            if hasattr(self.teams[i],"non-player"):
                continue
            teammoves=self.getallmoves(teams=[i])[2]
            if len(teammoves)==0:
                if self.game!=None:
                    self.game.teamlose(i)
        self.teamturn=turntemp
        self.pieceauth=authtemp
    
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
    def validatemove(self,x,y,team=0):
        if team not in self.pieceauth:
            return False
        if not 0<=x<self.WIDTH:
            return False
        if not 0<=y<self.HEIGHT:
            return False
        return True
    def updateallmoves(self,data=None,teams=[]):
        if not data:
            data=self.data
        for ystrip in data:
            for tile in ystrip:
                if not tile:
                    continue
                if tile.team not in teams:
                    continue
                tile.updateMoves(data,cc=True)
    def getallmoves(self,data=None,teams=[],teaminv=False):
        if not data:
            data=self.data
        takes=[]
        moves=[]
        for ystrip in data:
            for tile in ystrip:
                if not tile:
                    continue
                if teaminv:
                    if tile.team in teams:
                        continue
                else:
                    if tile.team not in teams:
                        continue
                temp= tile.getavailmoves(data)
                moves+=temp[0]
                takes+=temp[1]
        actions=moves+takes
        return moves,takes,actions
    def genboard():
        pass
    def addpiece(self,x,y,name,team,**kwargs):
        name=name.lower()
        if name not in self.PIECES:
            warnings.warn(f"Sprite not found for piece \"{name}\". Using dummy instead")
            name="dummy"
        if not 0<=x<len(self.data):
            warnings.warn("Out of bounds")
        if not 0<=y<len(self.data[x]):
            warnings.warn("Out of bounds")
        self.data[x][y]=self.PIECES[name](logic=self,x=x,y=y,team=team,**kwargs)
    def movepiece(self,pos1,pos2):
        origin=self.data[int(pos1.x)][int(pos1.y)]
        if not origin:
            return False
        action=origin.checkmove(pos2)
        if action != "return":
            origin.position=pos2
            self.data[int(pos1.x)][int(pos1.y)]=None
            self.data[int(pos2.x)][int(pos2.y)]=origin
            if self.game != None:
                self.game.endturn()
        return action
    def getpiece(self,x,y):
        return self.data[x][y]