import tkinter as tk
from tkinter import ttk
import vectormath

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
        self.data=[[None]*12]*12
        for x in range(0,width*tile,tile):
            for y in range(0,height*tile,tile):
                if (x+y)/10%2==0:
                    self.create_rectangle(x,y,x+tile,y+tile,fill="#865DFF",outline="")
                else:
                   self.create_rectangle(x,y,x+tile,y+tile,fill="#E384FF",outline="")
        self.data[0][0]=Piece(self,tile)
        self.draggable=None        
        pass
    def drag_stop(self,event):
        widget = self.draggable
        size=self.tilesize
        if not self.draggable:
            return
        x = (self.coords(widget.image)[0]+size//2)//size*size
        y = (self.coords(widget.image)[1]+size//2)//size*size
        widget.validatemove(x,y)
        self.draggable=None
    def drag_start(self,event):
        tilex=event.x//self.tilesize
        tiley=event.y//self.tilesize
        print(tilex,tiley)
        if 0<=tilex<self.width and 0<=tiley<self.height:
            if not self.data[tilex][tiley]:
                return
            self.draggable=self.data[tilex][tiley]
            self.draggable._drag_start_x = event.x
            self.draggable._drag_start_y = event.y

    def drag_motion(self,event):
        if not self.draggable:
            return
        widget = self.draggable
        x = event.x - self.coords(widget.image)[0] - self.tilesize//2
        y = event.y - self.coords(widget.image)[1] - self.tilesize//2
        self.move(widget.image,x,y)

class Piece():
    def __init__(self,board:Board,size) -> None:
        self.board=board
        self.sprite=tk.PhotoImage(file="Lol.ppm")
        self.image=board.create_rectangle(0,0,board.tilesize,board.tilesize,fill="#88A47C")
        board.tag_raise(self.image)
        print(self.image,self.sprite)
        self.tilesize=size
    def validatemove(self,x,y):
        pass


root=tk.Tk()
a=ttk.Frame(root)
a.pack()
Board(a,8,8,90).pack()
tk.mainloop()