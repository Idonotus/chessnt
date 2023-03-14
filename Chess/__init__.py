import tkinter as tk
from .Logic import GameLogic as logic
from .Graphics import GameGraphics as gui
from .Logic import GamecConductor as conductor


class Game:
    """Allows for communication between modules and generally parses things together"""
    def __init__(self,master=None,height=8,width=8,tile=50) -> None:
        if not master:
            master=tk.Tk()
        self.gui=gui.Gui(master,width,height,tile)
        self.gui.pack()
        self.logic=logic.Logic(width,height,2,self)
        self.gui.logic=self.logic
        self.conductor=conductor.Conductor([1,0])
        self.conductor.logic=self.logic
        self.end=False
    def addpiece(self,name,x,y,team,**kwargs):
        self.logic.addpiece(x=x,y=y,name=name,team=team,**kwargs)
        self.gui.addpiece(x=x,y=y,name=name,team=team)
    def endturn(self):
        if self.end:
            return
        self.logic.endcheck()
        if self.end:
            return
        self.conductor.newturn()
        self.logic.updateallmoves(teams=[0,1])
    def start(self):
        self.logic.updateallmoves(teams=[0])
    def teamlose(self,team):
        self.gui.end(team)
        self.conductor.end()
def make():
    g=Game(height=8,width=8,tile=60)
    g.addpiece("king",1,1,0)
    g.addpiece("king",3,3,1)
    g.addpiece("rook",3,2,1)
    g.addpiece("queen",7,7,0)
    g.start()
    tk.mainloop()