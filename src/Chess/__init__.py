import tkinter as tk
from . import Logic, Graphics, Stateloader, Turns



pieces={
    "c":"cpawn",
    "p":"pawn",
    "k":"king",
    "r":"rook",
    "q":"queen",
    "n":"knight",
    "b":"bishop"
}
classic="8x8|b|r0,n0,b0,q0,k0,k0,n0,r0|nr|p0*8|nr|o*8|nr|o*8|nr|o*8|nr|o*8|nr|p1*8|nr|r1,n1,b1,q1,k1,b1,n1,r1"
class Game:
    """Allows for communication between modules and generally parses things together"""
    def addpiece(self,name,x,y,team,**kwargs):
        self.logic.addpiece(x=x,y=y,name=name,team=team,**kwargs)
        self.gui.addpiece(x=x,y=y,name=name,team=team)
    def makemove(self,pos1,pos2):
        if not self.logic.canmove(pos1,pos2,team=True):
            return
        r=self.logic.reqmovepiece(pos1,pos2)
        if r is None:
            return
        self.gui.applychanges(r)
        self.endturn()
    def endturn(self):
        if self.end:
            return
        endteam=self.logic.endcheck()
        if endteam:
            self.teamlose(endteam)
            return
        if self.end:
            return
        self.logic.teamturn=next(self.conductor)
        self.logic.updateallmoves()
    def start(self):        
        self.logic.updateallmoves()
    def teamlose(self,team):
        self.gui.end(team)
        self.logic.teamturn=Turns.NULL_TURN
    def highlightmoves(self,x,y):
        p=self.logic.getpiece(x=x,y=y)
        if not p:
            return
        self.gui.highlighttiles(p.availmoves+p.availtakes,highlight="move")

    def signal(self,sig,*args,**kwargs):
        if sig=="drop_piece":
            self.makemove(*args)
        if sig=="pickup_piece":
            self.highlightmoves(*args)

    @staticmethod
    def blankboard(master,height=8,width=8,tile=50,numteams=2,turnorder=[0,1]):
        g=Game()
        if not master:
            master=tk.Tk()
        g.master=master
        g.gui=Graphics.Gui(master,width,height,tile,signal=g.signal)
        g.gui.pack()
        g.logic=Logic.Logic(width,height,numteams)
        g.conductor=Turns.TurnManager(turnorder)
        g.end=False
        return g
    
    @staticmethod
    def loadpresetboard(name):
        d=Stateloader.getBoard(name)
        return Game(d)

    def __init__(self,data):
        if not Stateloader.valid_data(data):
            raise TypeError
        sizedata=data["dim"]
        self.gui=Graphics.Gui.genboard(tk.Tk(),sizedata,data["boarddata"],self.signal)
        self.gui.pack()
        self.logic=Logic.Logic.genboard(data["numteams"],sizedata,data["boarddata"])
        self.conductor=Turns.TurnManager(data["turnorder"])
        self.end=False