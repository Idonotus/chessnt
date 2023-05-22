from .vectormath import *
from .Graphics.Piece import SpritePiece
import logging
import tkinter as tk
import json
import os


class Gui(tk.Canvas):
    """Handles chess GUI/user interaction"""
    def __init__(self, master, width=8,height=8,tile=50,signal=None) -> None:
        self.WIDTH=width
        self.HEIGHT=height
        self.TILESIZE=tile
        with open(os.path.join(os.path.dirname(__file__),"sprites.json")) as f:
            self.SPRITES=json.load(f)
        self.signal=signal
        self.highlights={"move":("#FFA3FD","#E384FF"),
                        "default":("#fcf803","#fcb603"),
                        "danger":("#E76161","#B04759"),
                        "normal":("#FFFFFF","#000000"),}
        super().__init__(master,height=(height)*tile,width=(width)*tile)
        self.bind("<Button-1>",self.drag_start)
        self.bind("<B1-Motion>",self.drag_motion)
        self.bind("<ButtonRelease-1>",self.drag_stop)
        self.data=[]
        self.teamcolors=["#FF0000","#0000FF"]
        self.tiles=[]
        self.game=None
        self.ROTATION=0
        self.draggable=None
        for x in range(width):
            self.data.append([])
            for _ in range(height):
                self.data[x].append(None)
        for x in range(0,self.WIDTH):
            self.tiles.append([])
            for y in range(0,self.HEIGHT):
                px,py=self.localrotate(self.ROTATION,x,y)
                scaledx=px*self.TILESIZE
                scaledy=py*self.TILESIZE
                colour=self.highlights["normal"][(x**2+y)%len(self.highlights["normal"])]


                rect=self.create_rectangle(scaledx,scaledy,scaledx+tile,scaledy+tile,fill=colour,outline="")
                self.tag_lower(rect)
                self.tiles[x].append(rect)
    
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

    def addpiece(self,name,x,y,team):
        if name not in self.SPRITES:
            logging.warn(f"Sprite not found for piece \"{name}\". Using dummy instead")
            name="dummy"
        if not 0<=x<len(self.data) or not 0<=y<len(self.data[x]):
            logging.warn(f"Coordinate x:{x} y:{y} of bounds")
            return
        p=SpritePiece(self,self.TILESIZE,x=x,y=y,team=team,sprite=self.SPRITES[name])
        self.data[x][y]=p
    
    def settile(self,x,y,name=None,team=None):
        if self.data[x][y]:
                self.data[x][y].delete()
        if name is None:
            return
        if team is None:
            return
        self.addpiece(name,x,y,team)

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

    def highlighttiles(self,tiles,*,color:list=[],highlight=""):
        if highlight not in self.highlights:
            if color is None or color == []:
                color=self.highlights["default"]
        else:
            color=self.highlights[highlight]
        for pos in tiles:
            if isinstance(pos,vector):
                fill=color[int(pos.x+pos.y)%len(color)]
                self.itemconfigure(self.tiles[int(pos.x)][int(pos.y)],fill=fill,tags=(highlight,))
    
    def applychanges(self,changes):
        for item in changes:
            if item[1]:
                self.settile(item[0][0],item[0][1],item[1]["name"],item[1]["team"])
            else:
                self.settile(item[0][0],item[0][1],None)

    def end(self,team):
        p=tk.Toplevel()
        tk.Label(p,text=f"Team {team+1} lost").pack()

    def placepiece(self,image,x,y,Piece):
        x,y=self.localrotate(self.ROTATION,x,y)
        xpos=x*self.TILESIZE
        ypos=y*self.TILESIZE
        
        xpos-=self.coords(image)[0]
        ypos-=self.coords(image)[1]
        if hasattr(Piece,"offset"):
            xpos+=Piece.offset[0]
            ypos+=Piece.offset[1]
        self.move(Piece.image,xpos,ypos)
    
    def drag_stop(self,event):
        widget = self.draggable
        size=self.TILESIZE
        if not self.draggable:
            return
        x = (self.coords(widget.image)[0]+size//2)
        y = (self.coords(widget.image)[1]+size//2)
        
        if hasattr(widget,"offset"):
            x-=widget.offset[0]
            y-=widget.offset[1]
        x/=size
        y/=size
        y=int(y)
        x=int(x)
        x,y=self.localrotate(self.ROTATION,x,y,True)
        self.draggable.returnpiece()
        self.draggable=None         
        self.removehighlight(highlight="move")
        pos2=vector(x,y)
        if self.signal:
            self.signal("drop_piece",widget.position,pos2)
        
    def drag_start(self,event):
        tilex=event.x//self.TILESIZE
        tiley=event.y//self.TILESIZE
        tilex,tiley=self.localrotate(self.ROTATION,tilex,tiley,True)
        if 0<=tilex<self.WIDTH and 0<=tiley<self.HEIGHT:
            if not self.data[tilex][tiley]:
                return
            self.draggable=self.data[tilex][tiley]
            
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