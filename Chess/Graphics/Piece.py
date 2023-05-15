from ..vectormath import *
import random
def randcolor():
    return f"#{random.randint(0,255):02x}{random.randint(0,255):02x}{random.randint(0,255):02x}"
class Piece():
    def __init__(self,gui,size,points,x=0,y=0,team=0):
        self.gui=gui
        self.position=vector(x,y)
        self.TILESIZE=size
        self.team=team
        if team < len(gui.teamcolors):
            color=gui.teamcolors[team]
        else:
            color=randcolor()
            gui.teamcolors.append(color)
        self.image=gui.create_polygon(*points,fill=color)
        self.returnpiece()

    def specialmoves(self,action,x,y):
        pass

    def move(self,actions,move):
        x=int(move.x)
        y=int(move.y)
        if isinstance(actions,str):
            actions=[actions]
        for action in actions:
            if action =="return":
                self.returnpiece()
            elif action=="take":
                self.takepiece(x,y)
            elif action=="move":
                self.movepiece(x,y)
            else:
                self.specialmoves(action,x,y)

    def delete(self):
        self.gui.delete(self.image)
        self.gui.data[int(self.position.x)][int(self.position.y)]=None

    def takepiece(self,x,y):
        self.gui.data[x][y].delete()
        self.movepiece(x,y)

    def returnpiece(self):
        pos=self.position
        self.gui.placepiece(self.image,pos.x,pos.y,self)

    def movepiece(self,x,y):
        pos=self.position
        self.gui.placepiece(self.image,x,y,self)
        self.gui.data[x][y]=self
        self.position=vector(x,y)
        self.gui.data[int(pos.x)][int(pos.y)]=None
