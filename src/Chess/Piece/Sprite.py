from ..vectormath import *
import random

def randcolor():
    r=random.randint(0,255)
    b=random.randint(0,255)
    g=random.randint(0,255)
    return f"#{r:02x}{b:02x}{g:02x}"

class Sprite:
    def __init__(self,gui,size,sprite,x=0,y=0,team=0):
        self.VISIBLE=True
        self.TILESIZE=size
        self.OFFSET=(vector(sprite["offset"][0],sprite["offset"][1])*size).intcoords()
        
        points=sprite["points"].copy()
        for i,item in enumerate(points):
            points[i]=(vector(item[0],item[1])*size+size*vector(x,y)).intcoords()
        self.gui=gui
        self.position=vector(x,y)
        
        self.team=team
        if team in gui.teamcolors:
            color=gui.teamcolors[team]
        else:
            color=randcolor()
            gui.teamcolors[team]=color
        self.image=gui.create_polygon(*points,fill=color)
        self.returnpiece()

    def delete(self):
        self.gui.delete(self.image)
        self.gui.data[int(self.position.x)][int(self.position.y)]=None
        self.VISIBLE=False

    def returnpiece(self):
        pos=self.position
        if self.VISIBLE:
            self.gui.placepiece(self,pos.x,pos.y)
