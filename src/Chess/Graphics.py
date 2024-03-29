
from .vectormath import *
from .Piece.Sprite import Sprite
import logging
import tkinter as tk
from . import assetLoader
import threading

class Gui(tk.Canvas):
    """Handles chess GUI/user interaction"""
    def __init__(self, master, width=8,height=8,tile=50,signal=None) -> None:
        self.WIDTH=width
        self.HEIGHT=height
        self.TILESIZE=tile
        self.RETURNDELAY=1000
        self.ROTATION=0
        self.SPRITES=assetLoader.getspritesheet("classic")
        self.signal=signal
        self.highlights={"move":("#FFA3FD","#E384FF"),
                        "default":("#fcf803","#fcb603"),
                        "danger":("#E76161","#B04759"),
                        "normal":("#FFFFFF","#000000"),
                        "temp":("#449966")}
        super().__init__(master,height=(height)*tile,width=(width)*tile)
        self.bind("<Button-1>",self.drag_start)
        self.bind("<B1-Motion>",self.drag_motion)
        self.bind("<ButtonRelease-1>",self.drag_stop)
        self.data=[]
        self.teamcolors={0:"#FF0000",1:"#0000FF",-1:"#444444"}
        self.tiles=[]
        self.draggable=None
        self.drawBoard()
    
    def drawBoard(self):
        self.data=[]
        for x in range(self.WIDTH):
            self.data.append([])
            for _ in range(self.HEIGHT):
                self.data[x].append(None)
        for x in range(0,self.WIDTH):
            self.tiles.append([])
            for y in range(0,self.HEIGHT):
                px,py=self.localrotate(self.ROTATION,x,y)
                scaledx=px*self.TILESIZE
                scaledy=py*self.TILESIZE
                colour=self.highlights["normal"][(x**2+y)%len(self.highlights["normal"])]
                rect=self.create_rectangle(scaledx,scaledy,
                                           scaledx+self.TILESIZE,
                                           scaledy+self.TILESIZE,
                                           fill=colour,outline="")
                self.tag_lower(rect)
                self.tiles[x].append(rect)

    @staticmethod
    def genboard(master,dim,boarddata,signal):
        g=Gui(master=master,width=dim[0],height=dim[1],signal=signal)
        if isinstance(boarddata[0],dict):
            for tile in boarddata:
                x, y=tile["pos"] 
                g.addpiece(x=x,y=y,**tile)
        if isinstance(boarddata[0],list):
            for ystrip in boarddata:
                for tile in ystrip:
                    if not tile:
                        continue
                    x, y=tile["pos"] 
                    g.addpiece(x=x,y=y,name=tile["name"],team=tile["team"])
        return g

    def setstylesheet(self,sheet):
        if not isinstance(sheet,dict):
            raise TypeError
        self.SPRITES=sheet
        if "dummy" not in self.SPRITES:
            self.SPRITES["dummy"]={"offset":[0,0],"points":[(0,0),(0,1),(1,1),(1,0)]}

    def setscheme(self,name,colors:tuple):
        if not isinstance(colors,(list,tuple)):
            raise TypeError
        self.highlights[name]=colors

    def addpiece(self,name,x,y,team,inactive=False,**kwargs):
        if name not in self.SPRITES:
            logging.warn(f"Sprite not found for piece \"{name}\". Using dummy instead")
            name="dummy"
        if not 0<=x<len(self.data) or not 0<=y<len(self.data[x]):
            logging.warn(f"Coordinate x:{x} y:{y} of bounds")
            return
        if inactive:
            team=-1
        p=Sprite(self,self.TILESIZE,x=x,y=y,team=team,sprite=self.SPRITES[name])
        self.data[x][y]=p
    
    def settile(self,x,y,name=None,team=None,**kwargs):
        if self.data[x][y]:
                self.data[x][y].delete()
        if name is None:
            return
        if team is None:
            return
        self.addpiece(name,x,y,team,**kwargs)

    def localrotate(self,rotation,x,y,inv=False):
        key=vector(1,1)
        v=vector(x,y)
        if inv:
            rotation=4-rotation
        key=key.rot90(rotation)
        v=v.rot90(rotation)
        x=int(v.x)
        y=int(v.y)
        if x<=0 and key.x<0:
            x=((self.WIDTH-1))+x
        if y<=0 and key.y<0:
            y=((self.HEIGHT-1))+y
        return x,y

    def removehighlight(self,highlight=None,tiles=[]):
        atiles=[]+tiles
        if highlight in self.highlights:
            atiles+=[vector(self.coords(obj)[0],self.coords(obj)[1])/self.TILESIZE for obj in self.find_withtag(highlight)]
        self.highlighttiles(atiles,highlight="normal")

    def highlightalltiles(self,highlight=""):
        if highlight not in self.highlights:
            highlight="default"
        color=self.highlights[highlight]
        for x,ystrip in enumerate(self.tiles):
            for y,tile in enumerate(ystrip):
                fill=color[(x+y)%len(color)]
                self.itemconfigure(tile,fill=fill,tags=(highlight,))

    def highlighttiles(self,tiles,*,color:list=[],highlight="",name=None):
        if not name:
            name=highlight
        if highlight not in self.highlights:
            if color is None or color == []:
                highlight="default"
                color=self.highlights["default"]
            else:
                highlight="temp"
        else:
            color=self.highlights[highlight]
        for pos in tiles:
            if isinstance(pos,vector):
                x,y=pos.intcoords()
                fill=color[(x+y)%len(color)]
                self.itemconfigure(self.tiles[x][y],fill=fill,tags=(name,))

    def applychanges(self,changes):
        for item in changes:
            if item[1]:
                self.settile(item[0][0],item[0][1],**item[1])
            else:
                self.settile(item[0][0],item[0][1],None)

    def end(self,team):
        p=tk.Toplevel()
        tk.Label(p,text=f"Team {team} lost").pack()

    def placepiece(self,Piece,x,y):
        x,y=self.localrotate(self.ROTATION,x,y)
        xpos=x*self.TILESIZE
        ypos=y*self.TILESIZE
        coords=self.coords(Piece.image)
        if not coords:
            return
        xpos-=coords[0]
        ypos-=coords[1]
        if hasattr(Piece,"OFFSET"):
            xpos+=Piece.OFFSET[0]
            ypos+=Piece.OFFSET[1]
        self.move(Piece.image,xpos,ypos)
    
    def drag_stop(self,event):
        widget = self.draggable
        size=self.TILESIZE
        if not self.draggable:
            return
        x = (self.coords(widget.image)[0]+size//2)
        y = (self.coords(widget.image)[1]+size//2)
        
        if hasattr(widget,"OFFSET"):
            x-=widget.OFFSET[0]
            y-=widget.OFFSET[1]
        x/=size
        y/=size
        y=int(y)
        x=int(x)
        x,y=self.localrotate(self.ROTATION,x,y,True)
        if self.RETURNDELAY>=0:
            self.after(self.RETURNDELAY, self.draggable.returnpiece)
        self.draggable=None         
        self.removehighlight(highlight="move")
        pos2=vector(x,y)
        if self.signal:
            self.signal("drop_piece",widget.position,pos2)

    def getpiece(self,x,y):
        if not(0<=x<self.WIDTH and 0<=y<self.HEIGHT):
            return None
        try:
            return self.data[x][y]
        except:
            return None

    def drag_start(self,event):
        tilex=event.x//self.TILESIZE
        tiley=event.y//self.TILESIZE
        tilex,tiley=self.localrotate(self.ROTATION,tilex,tiley,True)
        self.draggable=self.getpiece(tilex,tiley)
        if not self.draggable:
            return
        self.tag_raise(self.draggable.image)
        if self.signal:
            self.signal("pickup_piece",tilex,tiley)

    def drag_motion(self,event):
        if not self.draggable:
            return
        widget = self.draggable
        x = event.x - self.TILESIZE//2
        y = event.y - self.TILESIZE//2
        image=widget.image
        xpos=x-self.coords(image)[0]
        ypos=y-self.coords(image)[1]
        if hasattr(widget,"offset"):
            xpos+=widget.offset[0]
            ypos+=widget.offset[1]
        self.move(image,xpos,ypos)