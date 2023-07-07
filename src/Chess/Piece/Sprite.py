from ..vectormath import *
import random

def randcolor():
    return f"#{random.randint(0,255):02x}{random.randint(0,255):02x}{random.randint(0,255):02x}"

class Sprite:
    def __init__(self,gui,size,sprite,x=0,y=0,team=0):
        points=sprite["points"].copy()
        self.offset=(vector(sprite["offset"][0],sprite["offset"][1])*size).intcoords()
        for i,item in enumerate(points):
            points[i]=(vector(item[0],item[1])*size+size*vector(x,y)).intcoords()
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

    def delete(self):
        self.gui.delete(self.image)
        self.gui.data[int(self.position.x)][int(self.position.y)]=None

    def takepiece(self,x,y):
        self.gui.data[x][y].delete()
        self.movepiece(x,y)

    def returnpiece(self):
        pos=self.position
        self.gui.placepiece(self,pos.x,pos.y)

    def movepiece(self,x,y):
        pos=self.position
        self.gui.placepiece(self,x,y)
        self.gui.data[x][y]=self
        self.position=vector(x,y)
        self.gui.data[int(pos.x)][int(pos.y)]=None
