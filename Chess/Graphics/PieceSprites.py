from .Piece import Piece
class Pawn(Piece):
    def __init__(self, gui, size, x=0, y=0,direction=0,team=0) -> None:
        self.offset=(size*3.5/10,size/10)
        ax=x*size
        ay=y*size
        points=[
            (ax+size/10,ay+size/10),(ax+size/10,ay+size*4/10),(ax+size*2/10,ay+size*4/10),
            (ax+size/10,ay+size),(ax+size*4/10,ay+size),(ax+size*3/10,ay+size*4/10),
            (ax+size*4/10,ay+size*4/10),(ax+size*4/10,ay+size/10)    
                ]
        super().__init__(gui, size, points, x, y,team)
    def specialmoves(self,action, x, y):
        if action=="promote":
            self.delete()
            self.gui.addpiece("queen",x,y,self.team)
class Knife(Piece):
    def __init__(self, gui, size, x=0, y=0, team=0) -> None:
        ax=x*size
        ay=y*size
        self.offset=(size*3.5/10,size/10)
        points=[
            (ax,ay),(ax+size*.3,ay),(ax+size*.5,ay+size*0.2),(ax+size*.5,ay+size*.6),
            (ax+size*.4,ay+size*.7),(ax+size*.5,ay+size*.7),(ax+size/2,ay+size*4.5/5),
            (ax-size/5,ay+size*4.5/5),(ax-size/5,ay+size*3.5/5),(ax+size/10,ay+size*1.5/5),
            (ax-size/5,ay+size*2/5)
        ]
        super().__init__(gui, size, points, x, y, team)

class Rook(Piece):
    def __init__(self, gui, size, x=0, y=0, team=0) -> None:
        ax=x*size
        ay=y*size
        self.offset=(size*.1,size*.1)
        points=[(ax,ay),(ax+size*.8,ay),(ax+size*.8,ay+size*.3),(ax+size*.7,ay+size*.3),
                (ax+size*.7,ay+size*.9),(ax+size*.1,ay+size*.9),(ax+size*.1,ay+size*.3),
                (ax,ay+size*.3)]
        super().__init__(gui, size, points, x, y, team)

class Bishop(Piece):
    def __init__(self, gui, size, x=0, y=0, team=0) -> None:
        ax=x*size
        ay=y*size
        self.offset=(size*.5,size*.1)
        points=[
            (ax,ay),(ax+size*.3,ay+size*.4),(ax+size*.3,ay+size*.5),(ax+size*.1,ay+size*.7),
            (ax+size*.3,ay+size*.7),(ax+size*.3,ay+size*.9),(ax+size*-.3,ay+size*.9),
            (ax+size*-.3,ay+size*.7),(ax+size*-.1,ay+size*.7),(ax+size*-.3,ay+size*.5),
            (ax+size*-.3,ay+size*.4),(ax,ay+size*.5),(ax+size*-.1,ay+size*.2),
                ]
        super().__init__(gui, size, points, x, y, team)

class Queen(Piece):
    def __init__(self, gui, size, x=0, y=0, team=0) -> None:
        ax=x*size
        ay=y*size
        self.offset=(0,size*.2)
        points=[
            (ax,ay),(ax+size*.5,ay+size*.3),(ax+size,ay),(ax+size*.8,ay+size*.6),(ax+size*.9,ay+size*.6),
            (ax+size*.9,ay+size*.8),(ax+size*.1,ay+size*.8),(ax+size*.1,ay+size*.6),
            (ax+size*.2,ay+size*.6)
                ]
        super().__init__(gui, size, points, x, y, team)

class King(Piece):
    def __init__(self, gui, size, x=0, y=0,direction=0,team=0) -> None:
        self.offset=(0,size*.2)
        self.direction=direction
        ax=x*size
        ay=y*size
        points=[
            (ax,ay),(ax+size,ay),(ax+size*.8,ay+size*.6),(ax+size*.9,ay+size*.6),
            (ax+size*.9,ay+size*.8),(ax+size*.1,ay+size*.8),(ax+size*.1,ay+size*.6),
            (ax+size*.2,ay+size*.6)
                ]
        super().__init__(gui, size, points, x, y,team)
def getallpieces():
    return {
        "cpawn":Pawn,
        "pawn":Pawn,
        "knight":Knife,
        "rook":Rook,
        "queen":Queen,
        "king":King,
        "bishop":Bishop
    }
