import tkinter as tk
from tkinter import ttk
from vectormath import *

class Board(tk.Canvas):
    def __init__(self, master, width=8,height=8,tile=50) -> None:
        self.width=width
        self.height=height
        self.tilesize=tile
        super().__init__(master,height=height*tile,width=width*tile)
        self.bind("<Button-1>",self.drag_start)
        self.bind("<B1-Motion>",self.drag_motion)
        self.bind("<ButtonRelease-1>",self.drag_stop)
        self.framelayer=self.create_window(0,0)
        self.data=[]
        self.teamcolours=["#CBE4DE","#FF0000","#0000FF"]
        for x in range(width):
            self.data.append([])
            for _ in range(height):
                self.data[x].append(None)
        for x in range(0,width):
            for y in range(0,height):
                scaledx=x*tile
                scaledy=y*tile
                if (x+y)%2==0:

                    self.create_rectangle(scaledx,scaledy,scaledx+tile,scaledy+tile,fill="#000000",outline="")
                else:
                   self.create_rectangle(scaledx,scaledy,scaledx+tile,scaledy+tile,fill="#FFFFFF",outline="")
        self.data[0][0]=Knife(self,tile,0,0,team=2)
        self.data[1][1]=Pawn(self,tile,1,1,team=1)
        self.data[2][2]=Rook(self,tile,2,2,0)
        self.draggable=None        
        pass
    
    def placepiece(self,image,x,y,Piece):
        
        xpos=x*self.tilesize-self.coords(image)[0]
        ypos=y*self.tilesize-self.coords(image)[1]
        if hasattr(Piece,"offset"):
            xpos+=Piece.offset[0]
            ypos+=Piece.offset[1]
        self.move(Piece.image,xpos,ypos)

    

    def validatemove(self,x,y):
        if not 0<=x<self.width:
            return False
        if not 0<=y<self.height:
            return False
        return True
    def drag_stop(self,event):
        widget = self.draggable
        size=self.tilesize
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
        widget.move(x,y)
        self.draggable=None
    def drag_start(self,event):
        tilex=event.x//self.tilesize
        tiley=event.y//self.tilesize
        if 0<=tilex<self.width and 0<=tiley<self.height:
            if not self.data[tilex][tiley]:
                return
            self.draggable=self.data[tilex][tiley]
            self.tag_raise(self.draggable.image)

    def drag_motion(self,event):
        if not self.draggable:
            return
        widget = self.draggable
        x = event.x - self.tilesize//2
        y = event.y - self.tilesize//2
        self.placepiece(widget.image,x/self.tilesize,y/self.tilesize,widget)

class Piece():
    def __init__(self,board:Board,size,x=0,y=0,team=0) -> list[vector]:
        self.board=board
        self.position=vector(x,y)
        
        self.tilesize=size
        self.team=team
    def validatemove(self,x,y):
        return "move"
    
    def line(self,end,step,start=vector(0,0)):
        print(start/step)
        try:
            localend=end/step
            localstart=start/step
        except:
            return []
        if localend<localstart:
            sign=-1
        else:
            sign=1
        group=[]
        for scale in range(localstart+sign,localend,sign):
            group.append(step*scale)
        return group
    def move(self,x,y):
        if  not self.board.validatemove(x,y):
            self.returnpiece()
            return
        action=self.validatemove(x,y)
        if action=="move":
            self.movepiece(x,y)
        elif action=="take":
            self.takepiece(x,y)
        elif action=="return":
            self.returnpiece()
    
    def takepiece(self,x,y):
        img=self.board.data[x][y].image
        self.board.delete(img)
        self.movepiece(x,y)

    def returnpiece(self):
        pos=self.position
        self.board.placepiece(self.image,pos.x,pos.y,self)

    def movepiece(self,x,y):
        pos=self.position
        self.board.placepiece(self.image,x,y,self)
        self.board.data[x][y]=self
        self.position=vector(x,y)
        self.board.data[int(pos.x)][int(pos.y)]=None

class Pawn(Piece):
    def __init__(self, board: Board, size, x=0, y=0,direction=0,team=0) -> None:
        self.moves=(vector(0,1).rot90(direction),)
        self.takes=(vector(1,1).rot90(direction),vector(-1,1).rot90(direction))
        self.offset=(size*3.5/10,size/10)
        self.startmove=vector(0,2).rot90(direction)
        self.direction=direction
        ax=x*size
        ay=y*size
        points=[
            (ax+size/10,ay+size/10),(ax+size/10,ay+size*4/10),(ax+size*2/10,ay+size*4/10),
            (ax+size/10,ay+size),(ax+size*4/10,ay+size),(ax+size*3/10,ay+size*4/10),
            (ax+size*4/10,ay+size*4/10),(ax+size*4/10,ay+size/10)    
                ]
        self.image=board.create_polygon(*points,fill=board.teamcolours[team])
        super().__init__(board, size, x, y,team)
        self.returnpiece()
    def validatemove(self, x, y):
        move=self.position-vector(x,y)
        if move==self.startmove:
            self.startmove=False
            return "move"
        if self.board.data[x][y] and move in self.takes:
            if self.board.data[x][y].team!=self.team:
                return "take"
            else:
                return "return"
        elif move in self.moves:
            return "move"
        else:
            return "return"
class Knife(Piece):
    def __init__(self, board: Board, size, x=0, y=0, team=0) -> None:
        ax=x*size
        ay=y*size
        self.moves=vector(1,2).all90()+vector(-1,2).all90()
        self.offset=(size*3.5/10,size/10)
        points=[
            (ax,ay),(ax+size*.3,ay),(ax+size*.5,ay+size*0.2),(ax+size*.5,ay+size*.6),
            (ax+size*.4,ay+size*.7),(ax+size*.5,ay+size*.7),(ax+size/2,ay+size*4.5/5),
            (ax-size/5,ay+size*4.5/5),(ax-size/5,ay+size*3.5/5),(ax+size/10,ay+size*1.5/5),
            (ax-size/5,ay+size*2/5)
        ]
        self.image=board.create_polygon(*points,fill=board.teamcolours[team])
        super().__init__(board, size, x, y, team)
        self.returnpiece()
    def validatemove(self, x, y):
        move=self.position-vector(x,y)
        if move not in self.moves:
            return "return"
        if not self.board.data[x][y]:
            return "move"
        if self.board.data[x][y]!=self.team:
            return "take"
        return "return"
class Rook(Piece):
    def __init__(self, board: Board, size, x=0, y=0, team=0) -> None:
        ax=x*size
        ay=y*size
        self.offset=(size*.1,size*.1)
        points=[(ax,ay),(ax+size*.8,ay),(ax+size*.8,ay+size*.3),(ax+size*.7,ax+size*.3),
                (ax+size*.7,ay+size*.9),(ax+size*.1,ay+size*.9),(ax+size*.1,ax+size*.3),
                (ax,ay+size*.3)]
        self.image=board.create_polygon(*points,fill=board.teamcolours[team])
        super().__init__(board, size, x, y, team)
        self.returnpiece()
    def validatemove(self, x, y):
        move=vector(x,y)
        travel_line=self.line(move,vector(0,1),self.position)+self.line(move,vector(1,0),self.position)
        if len(travel_line):
            return "return"
        for pos in travel_line:
            if self.board.data[int(pos.x)][int(pos.y)]:
                return "return"
        if self.board.data[x][y]:
            if self.board.data[x][y].team!=self.team:
                return "return"
            return "take"
        return "move"

root=tk.Tk()
Board(root,9,9,100).pack()
tk.mainloop()