import tkinter as tk
from . import GameLogic as logic
from . import GameGraphics as gui


def turngen(turnorder:list):
    while True:
        t=turnorder.pop(0)
        if not isinstance(t,(list,tuple)):
            t=(t,)
        turnorder.append(t)
        yield t
class TurnIter:
    def __init__(self,turnorder:list) -> None:
        self.torder=turnorder
    def validateorder(self):
        for i,o in enumerate(self.torder):
            if not isinstance(o,(tuple,list,int)):
                raise TypeError
            if isinstance(o,(int)):
                self.torder[i]=[o]
    def __setattr__(self, __name: str, __value) -> None:
        o=self.torder
        super().__setattr__(__name,__value)
        if __name=="torder":
            try:
                self.validateorder()
            except:
                self.torder=o
    def __iter__(self):
        return self
    def deactiveteam(self,teamid:int):
        self.validateorder()
        t=[]
        for i,o in enumerate(self.torder):
            if teamid in o:
                for i,item in enumerate(o):
                    if item==teamid:
                        item+=1
                        item*=-1
                    o[i]=item
            t.append(o)
        self.torder=t

    def activeteam(self,teamid: int):
        self.validateorder()
        t=[]
        for i,o in enumerate(self.torder):
            if teamid in o:
                for i,item in enumerate(o):
                    if ((item*-1)-1)==teamid:
                        item+=1
                        item*=-1
                    o[i]=item
            t.append(o)
        self.torder=t
    def __next__(self):
        a=True
        while a:
            t=self.torder.pop(0)
            self.torder.append(t)
            for i in t:
                if i>=0:
                    a=False
                    break
        yield t

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
    def __init__(self,master=None,height=8,width=8,tile=50) -> None:
        if not master:
            master=tk.Tk()
        self.gui=gui.Gui(master,width,height,tile,signal=self.signal)
        self.gui.pack()
        self.logic=logic.Logic(width,height,2,self)
        self.conductor=turngen([1,0])
        self.end=False
    def addpiece(self,name,x,y,team,**kwargs):
        self.logic.addpiece(x=x,y=y,name=name,team=team,**kwargs)
        self.gui.addpiece(x=x,y=y,name=name,team=team)
    def makemove(self,pos1,pos2):
        if self.logic.canmove(pos1,pos2):
            return
        r=self.logic.movepiece(pos1,pos2)
        if r is None:
            return
        self.gui.applychanges(r)
        self.endturn()
    def endturn(self):
        if self.end:
            return
        self.logic.endcheck()
        if self.end:
            return
        self.logic.teamturn=next(self.conductor)
        self.logic.updateallmoves()
    def start(self):        
        self.logic.updateallmoves()
    def teamlose(self,team):
        self.gui.end(team)
        self.logic.teamturn=[-1]
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
def makeclassic():
    makeboard(classic)

def makeboard(data):
    data=data.split("|b|")
    sizedata=data[0].split("x")
    g=Game(master=tk.Tk(),width=int(sizedata[0]),height=int(sizedata[1]),tile=75)
    for y,row in enumerate(data[1].split("|nr|")):
        x=0
        for tile in row.split(","):
            places=1
            p=tile
            if "*" in tile:
                tile=tile.split("*")
                p=tile[0]
                places=int(tile[1])
            for _ in range(places):
                if p[0]=="o":
                    continue
                g.addpiece(pieces[p[0]],x,y,int(p[1]))
                x+=1
    g.start()
    tk.mainloop()