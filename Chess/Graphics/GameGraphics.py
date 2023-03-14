from ..vectormath import *
from . import PieceSprites
import warnings
import tkinter as tk
class Gui(tk.Canvas):
    """Handles chess GUI/user interaction"""
    def __init__(self, master, width=8,height=8,tile=50) -> None:
        self.WIDTH=width
        self.HEIGHT=height
        self.TILESIZE=tile
        self.colour=("#FFFFFF","#000000")
        self.movehighlights=("#E384FF","#FFA3FD")
        super().__init__(master,height=(height)*tile,width=(width)*tile)
        self.bind("<Button-1>",self.drag_start)
        self.bind("<B1-Motion>",self.drag_motion)
        self.bind("<ButtonRelease-1>",self.drag_stop)
        self.data=[]
        self.teamcolours=("#FF0000","#0000FF")
        self.tiles=[]
        self.logic=None
        self.ROTATION=0
        self.draggable=None 
        self.movehighlight=[]
        self.PIECES = PieceSprites.getallpieces()
        for x in range(width):
            self.data.append([])
            for _ in range(height):
                self.data[x].append(None)
        for x in range(0,self.WIDTH):
            self.tiles.append([])
            for y in range(0,self.HEIGHT):
                px,py=self.localrotate(self.ROTATION,x,
                                                 y)
                scaledx=px*self.TILESIZE
                scaledy=py*self.TILESIZE
                colour=self.colour[(x+y)%len(self.colour)]


                rect=self.create_rectangle(scaledx,scaledy,scaledx+tile,scaledy+tile,fill=colour,outline="")
                self.tag_lower(rect)
                self.tiles[x].append(rect)
        
    def addpiece(self,name,x,y,team):
        if name not in self.PIECES:
            warnings.warn(f"Sprite not found for piece \"{name}\". Using dummy instead")
            name="dummy"
        if not 0<=x<len(self.data):
            warnings.warn("Out of bounds")
            return
        if not 0<=y<len(self.data[x]):
            warnings.warn("Out of bounds")
            return
        self.data[x][y]=self.PIECES[name](self,self.TILESIZE,x=x,y=y,team=team)
    
    

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
    def removehighlight(self,highlight,tiles=[]):
        if not tiles:
            for pos in highlight:
                fill=self.colour[int(pos.x+pos.y)%len(self.colour)]
                self.itemconfigure(self.tiles[int(pos.x)][int(pos.y)],fill=fill)

    def highlighttiles(self,highlight:list,tiles):
        for pos in tiles:
            if isinstance(pos,vector):
                fill=self.movehighlights[int(pos.x+pos.y)%len(self.movehighlights)]
                self.itemconfigure(self.tiles[int(pos.x)][int(pos.y)],fill=fill)
            highlight.append(pos)

    def end(self,team):
        p=tk.Toplevel()
        tk.Label(p,text=f"Team {team+1} lost\nL BOZO").pack()
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
        a="return"
        pos2=vector(x,y)
        if self.logic:
            a=self.logic.movepiece(widget.position,pos2)
        
        match a:
            case "return":
                self.draggable.returnpiece()
            case "move":
                self.draggable.movepiece(x,y)
            case "take":
                self.draggable.takepiece(x,y)
        self.draggable=None         
        self.removehighlight(self.movehighlight)
    def drag_start(self,event):
        tilex=event.x//self.TILESIZE
        tiley=event.y//self.TILESIZE
        tilex,tiley=self.localrotate(self.ROTATION,tilex,tiley,True)
        if 0<=tilex<self.WIDTH and 0<=tiley<self.HEIGHT:
            if not self.data[tilex][tiley]:
                return
            self.draggable=self.data[tilex][tiley]
            w=self.draggable
            if self.logic:
                p=self.logic.getpiece(tilex,tiley)
                self.highlighttiles(self.movehighlight,p.availmoves+p.availtakes)
            self.tag_raise(self.draggable.image)

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