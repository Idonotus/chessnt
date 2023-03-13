from ..vectormath import *
class Piece():
    def __init__(self,gui,size,points,x=0,y=0,team=0):
        self.gui=gui
        self.position=vector(x,y)
        self.TILESIZE=size
        self.team=team
        self.image=gui.create_polygon(*points,fill=gui.teamcolours[team])
        self.returnpiece()


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
