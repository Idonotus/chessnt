import tkinter as tk
from tkinter import ttk
from Chess.vectormath import *
class Board(tk.Canvas):
    def __init__(self, master, width=8,height=8,tile=50) -> None:
        self.WIDTH=width
        self.HEIGHT=height
        self.peiceauth=[0,1,2]
        self.teamturn=[0,1,2]
        self.TILESIZE=tile
        self.colour=["#191825","#865DFF"]
        self.highlights=["#E384FF","#FFA3FD"]
        super().__init__(master,height=(height)*tile,width=(width)*tile)
        self.bind("<Button-1>",self.drag_start)
        self.bind("<B1-Motion>",self.drag_motion)
        self.bind("<ButtonRelease-1>",self.drag_stop)
        self.data=[]
        self.teamcolours=["#FF0000","#0000FF"]
        self.tiles=[]
        self.teamdata={"kings":[],"checks":[],"teams":[]}
        for i in range(len(self.teamcolours)):
            self.teamdata["teams"].append(i)
            self.teamdata["kings"].append([])
            self.teamdata["checks"].append(False)
        self.ROTATION=0
        for x in range(width):
            self.data.append([])
            for _ in range(height):
                self.data[x].append(None)
        for x in range(0,width):
            self.tiles.append([])
            for y in range(0,height):
                px,py=self.localrotate(self.ROTATION,x,
                                                 y)
                scaledx=px*tile
                scaledy=py*tile
                colour=self.colour[(x+y)%len(self.colour)]


                rect=self.create_rectangle(scaledx,scaledy,scaledx+tile,scaledy+tile,fill=colour,outline="")
                self.tiles[x].append(rect)
        self.data[5][0]=King(self,tile,5,0,team=1)
        self.data[0][0]=Knife(self,tile,0,0,team=0)
        for x in range(width):
            self.data[x][1]=Pawn(self,tile,x,1,direction=0,team=1)
        self.data[2][2]=Rook(self,tile,2,2,0)
        self.data[3][3]=Queen(self,tile,3,3,0)
        self.draggable=None 
        self.movehighlight=[]       
        self.propogateMove()
        self.PIECES={
            "pawn":Pawn,
            "knight":Knife,
            "queen":Queen,
            "bishop":Bishop,
            "rook":Rook
        }
        pass
    def addpiece(self,name,x,y,**kwargs):
        pass
    
    

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
                fill=self.highlights[int(pos.x+pos.y)%len(self.highlights)]
                self.itemconfigure(self.tiles[int(pos.x)][int(pos.y)],fill=fill)
            highlight.append(pos)

    def propogateMove(self,data=None,teams=None,teaminv=False):
        if not teams:
            teams=self.teamdata["teams"]
        elif teaminv:
            teams=[ateam for ateam in self.teamdata["teams"] if ateam not in teams]
        if not data:
            data=self.data
        moves=[]
        for ystrip in data:
            for tile in ystrip:
                if not tile:
                    continue
                if tile.team not in teams:
                    continue
                moves+= tile.updateMoves(data)
        return moves

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

    

    def validatemove(self,x,y,team=0):
        if team not in self.peiceauth:
            return False
        if team not in self.teamturn:
            return False
        if not 0<=x<self.WIDTH:
            return False
        if not 0<=y<self.HEIGHT:
            return False
        return True
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
        widget.move(x,y)
        self.draggable=None
        self.removehighlight(self.movehighlight)
        self.propogateMove()
    def drag_start(self,event):
        tilex=event.x//self.TILESIZE
        tiley=event.y//self.TILESIZE
        tilex,tiley=self.localrotate(self.ROTATION,tilex,tiley,True)
        if 0<=tilex<self.WIDTH and 0<=tiley<self.HEIGHT:
            if not self.data[tilex][tiley]:
                return
            self.draggable=self.data[tilex][tiley]
            w=self.draggable
            self.highlighttiles(self.movehighlight,w.availmoves+w.availtakes)
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

    def makecopy(self):
        copy=[]
        for n,ystrip in enumerate(self.data):
            copy.append([])
            for tile in ystrip:

                copy[n].append(tile)
        return copy

class Piece():
    def __init__(self,board:Board,size,points,x=0,y=0,team=0):
        self.board=board
        self.position=vector(x,y)
        self.availmoves=[]
        self.availtakes=[]
        self.TILESIZE=size
        self.team=team
        self.image=board.create_polygon(*points,fill=board.teamcolours[team])
        self.returnpiece()

    def validatemove(self,x,y,):
        move=vector(x,y)
        if move in self.availmoves:
            return "move"
        if move in self.availtakes:
            return "take"
        return "return"
    
    def line(self,end,step,start=vector(0,0)):
        localend=end-start
        rangeend=localend/step
        if rangeend is False:
            return []
        if rangeend<0:
            sign=-1
        else:
            sign=1
        if int(rangeend)!=rangeend:
            return []
        group=[]
        for scale in range(sign,int(rangeend)+sign,sign):
            group.append(step*scale+start)
        return group
    def move(self,x,y):
        if vector(x,y)==self.position:
            self.returnpiece()
            return
        if  not self.board.validatemove(x,y,self.team):
            self.returnpiece()
            return
        action=self.validatemove(x,y)
        if action=="move":
            self.movepiece(x,y)
        elif action=="take":
            self.takepiece(x,y)
        elif action=="return":
            self.returnpiece()

    def delete(self):
        self.board.delete(self.image)
        self.board.data[int(self.position.x)][int(self.position.y)]

    def takepiece(self,x,y):
        self.board.data[x][y].delete()
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
    def updateMoves(self,boarddata,availmoves,availtakes):
        if boarddata==self.board.data:
            self.availmoves=self.checkcheck(availmoves)
            self.availtakes=self.checkcheck(availtakes)
        return availmoves+availtakes
    def checkcheck(self,moves):
        data=self.board.makecopy()
        x=int(self.position.x)
        y=int(self.position.y)
        data[x][y]=None
        safemoves=[]
        for move in moves:
            data[int(move.x)][int(move.y)]=self
            possiblemoves=self.board.propogateMove(data,teams=[self.team],teaminv=True)
            unsafe=False
            for king in self.board.teamdata["kings"][self.team]:
                if king.position in possiblemoves:
                    unsafe=True
                    break
            if not unsafe:
                safemoves.append(move)
            data[int(move.x)][int(move.y)]=None
        return safemoves


class Pawn(Piece):
    def __init__(self, board: Board, size, x=0, y=0,direction=0,team=0) -> None:
        self.moves=(vector(0,1).rot90(direction),)
        self.takes=(vector(1,1).rot90(direction),vector(-1,1).rot90(direction))
        self.offset=(size*3.5/10,size/10)
        self.startmove=(vector(0,2).rot90(direction),)
        self.direction=direction
        ax=x*size
        ay=y*size
        points=[
            (ax+size/10,ay+size/10),(ax+size/10,ay+size*4/10),(ax+size*2/10,ay+size*4/10),
            (ax+size/10,ay+size),(ax+size*4/10,ay+size),(ax+size*3/10,ay+size*4/10),
            (ax+size*4/10,ay+size*4/10),(ax+size*4/10,ay+size/10)    
                ]
        super().__init__(board, size, points, x, y,team)
    def updateMoves(self,boarddata):
        availmoves=[]
        availtakes=[] 
        for move in self.startmove+self.moves:
            move+=self.position
            if not self.board.validatemove(move.x,move.y,self.team):
                continue
            if boarddata[int(move.x)][int(move.y)]:
                continue
            availmoves.append(move)
        for take in self.takes:
            take+=self.position
            if not self.board.validatemove(take.x,take.y,self.team):
                continue
            if not boarddata[int(take.x)][int(take.y)]:
                continue
            if boarddata[int(take.x)][int(take.y)].team==self.team:
                continue
            availtakes.append(take)
        return super().updateMoves(boarddata,availmoves,availtakes)
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
        super().__init__(board, size, points, x, y, team)
    def updateMoves(self,boarddata):
        availmoves=[]
        availtakes=[]
        for move in self.moves:
            move+=self.position
            if not self.board.validatemove(move.x,move.y,self.team):
                continue
            if boarddata[int(move.x)][int(move.y)]:
                if boarddata[int(move.x)][int(move.y)].team==self.team:
                    continue
                availtakes.append(move)
                continue
            availmoves.append(move)
        return super().updateMoves(boarddata,availmoves,availtakes)
class Rook(Piece):
    def __init__(self, board: Board, size, x=0, y=0, team=0) -> None:
        ax=x*size
        ay=y*size
        self.lines=vector(0,1).all90()
        self.offset=(size*.1,size*.1)
        points=[(ax,ay),(ax+size*.8,ay),(ax+size*.8,ay+size*.3),(ax+size*.7,ax+size*.3),
                (ax+size*.7,ay+size*.9),(ax+size*.1,ay+size*.9),(ax+size*.1,ax+size*.3),
                (ax,ay+size*.3)]
        super().__init__(board, size, points, x, y, team)
    def updateMoves(self,boarddata):
        availmoves=[]
        availtakes=[]
        for direction in self.lines:
            searchpos=self.position
            while True:
                searchpos+=direction
                if not self.board.validatemove(searchpos.x,searchpos.y,self.team):
                    break
                if boarddata[int(searchpos.x)][int(searchpos.y)]:
                    if boarddata[int(searchpos.x)][int(searchpos.y)].team!=self.team:
                        availtakes.append(searchpos)
                    break
                availmoves.append(searchpos)
        return super().updateMoves(boarddata,availmoves,availtakes)
class Bishop(Piece):
    def __init__(self, board: Board, size, x=0, y=0, team=0) -> None:
        ax=x*size
        ay=y*size
        self.lines=vector(1,1).all90()
        self.offset=(size*.5,size*.1)
        points=[
            (ax,ay),(ax+size*.3,ay+size*.4),(ax+size*.3,ay+size*.5),(ax+size*.1,ay+size*.7),
            (ax+size*.3,ay+size*.7),(ax+size*.3,ay+size*.9),(ax+size*-.3,ay+size*.9),
            (ax+size*-.3,ay+size*.7),(ax+size*-.1,ay+size*.7),(ax+size*-.3,ay+size*.5),
            (ax+size*-.3,ay+size*.4),(ax,ay+size*.5),(ax+size*-.1,ay+size*.2),
                ]
        super().__init__(board, size, points, x, y, team)
    def updateMoves(self,boarddata):
        availmoves=[]
        availtakes=[]
        for direction in self.lines:
            searchpos=self.position
            while True:
                searchpos+=direction
                if not self.board.validatemove(searchpos.x,searchpos.y,self.team):
                    break
                if boarddata[int(searchpos.x)][int(searchpos.y)]:
                    if boarddata[int(searchpos.x)][int(searchpos.y)].team!=self.team:
                        availtakes.append(searchpos)
                    break
                availmoves.append(searchpos)
        return super().updateMoves(boarddata,availmoves,availtakes)
class Queen(Piece):
    def __init__(self, board: Board, size, x=0, y=0, team=0) -> None:
        ax=x*size
        ay=y*size
        self.lines=vector(1,1).all90()+vector(0,1).all90()
        self.offset=(size*.5,size*.1)
        points=[
            (ax,ay),(ax+size*.3,ay+size*.4),(ax+size*.3,ay+size*.5),(ax+size*.1,ay+size*.7),
            (ax+size*.3,ay+size*.7),(ax+size*.3,ay+size*.9),(ax+size*-.3,ay+size*.9),
            (ax+size*-.3,ay+size*.7),(ax+size*-.1,ay+size*.7),(ax+size*-.3,ay+size*.5),
            (ax+size*-.3,ay+size*.4),(ax,ay+size*.5),(ax+size*-.1,ay+size*.2),
                ]
        super().__init__(board, size, points, x, y, team)
    def updateMoves(self,boarddata):
        availmoves=[]
        availtakes=[]
        for direction in self.lines:
            searchpos=self.position
            while True:
                searchpos+=direction
                if not self.board.validatemove(searchpos.x,searchpos.y,self.team):
                    break
                if boarddata[int(searchpos.x)][int(searchpos.y)]:
                    if boarddata[int(searchpos.x)][int(searchpos.y)].team!=self.team:
                        availtakes.append(searchpos)
                    break
                availmoves.append(searchpos)
        return super().updateMoves(boarddata,availmoves,availtakes)

class King(Piece):
    def __init__(self, board: Board, size, x=0, y=0,direction=0,team=0) -> None:
        self.moves=vector(0,1).all90()+vector(1,1).all90()
        self.offset=(size*3.5/10,size/10)
        self.direction=direction
        ax=x*size
        ay=y*size
        points=[
            (ax+size/10,ay+size/10),(ax+size/10,ay+size*4/10),(ax*2/10,ay+size*4/10),
            (ax+size/10,ay+size),(ax+size*4/10,ay+size),(ax+size*3/10,ay*4/10),
            (ax+size*4/10,ay+size*4/10),(ax+size*4/10,ay+size/10)    
                ]
        board.teamdata["kings"][team].append(self)
        super().__init__(board, size, points, x, y,team)
    def updateMoves(self,boarddata):
        availmoves=[]
        availtakes=[] 
        for move in self.moves:
            move+=self.position
            if not self.board.validatemove(move.x,move.y,self.team):
                continue
            if boarddata[int(move.x)][int(move.y)]:
                if boarddata[int(move.x)][int(move.y)].team==self.team:
                    continue
                availtakes.append(move)
            else:
                availmoves.append(move)
        return super().updateMoves(boarddata,availmoves,availtakes)
    def checkcheck(self,moves):
        data=self.board.makecopy()
        x=int(self.position.x)
        y=int(self.position.y)
        data[x][y]=None
        safemoves=[]
        for move in moves:
            takenpiece=data[int(move.x)][int(move.y)]
            data[int(move.x)][int(move.y)]=self
            possiblemoves=self.board.propogateMove(data,teams=[self.team],teaminv=True)
            unsafe=False
            for king in self.board.teamdata["kings"][self.team]:
                if king is self:
                    if move in possiblemoves:
                        unsafe=True
                        break
                elif king.position in possiblemoves:
                    unsafe=True
                    break
            if not unsafe:
                safemoves.append(move)
            data[int(move.x)][int(move.y)]=takenpiece
        return safemoves
root=tk.Tk()
Board(root,8,8,100).pack()
tk.mainloop()