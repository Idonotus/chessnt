import math
import typing
class vector:
    def __init__(self,x:typing.Union[int,float],y:typing.Union[int,float]) -> None:
        self.x=float(x)
        self.y=float(y)
    def __add__(self,obj):
        if not isinstance(obj,vector):
            raise TypeError(f"Cannot add vector and {type(obj)}")
        return vector(self.x+obj.x,self.y+obj.y)
    def __sub__(self,obj):
        if not isinstance(obj,vector):
            raise TypeError(f"Cannot add vector and {type(obj)}")
        return vector(self.x-obj.x,self.y-obj.y)
    def __mul__(self,obj:typing.Union[int,float]):
        return vector(self.x*obj,self.y*obj)
    def __rmul__(self,obj:typing.Union[int,float]):
        return vector(self.x*obj,self.y*obj)
    def __truediv__(self,obj:typing.Union[int,float]):
        if isinstance(obj,(int,float)):
            return vector(self.x/obj,self.y/obj)
        elif isinstance(obj,vector):
            if obj.x==0 and obj.y==0:
                raise ZeroDivisionError
            if obj.x==0:
                if self.x!=0:
                    return False
                return self.y/obj.y
            if obj.y==0:
                if self.y!=0:
                    return False
                return self.x/obj.x
            if self.x/obj.x!=self.y/obj.y:
                return False
            return self.x/obj.x
    def __repr__(self) -> str:
        return f"<vector object x:{self.x} y:{self.y} length:{self.length()}>"
    def __eq__(self, __o: object) -> bool:
        if isinstance(__o,tuple):
            if len(__o)!=2:
                return False
            return __o[0]==self.x and __o[1]==self.y
        elif isinstance(__o,vector):
            return __o.x==self.x and __o.y==self.y
        else:
            return False
    def length(self):
        return math.sqrt(abs(self.x)**2+abs(self.y)**2)
    def rotate(self,angle:typing.Union[int,float]):
        angle=math.radians(angle)
        return vector(
            self.x*math.cos(angle)+self.y*math.sin(angle),
            self.y*math.cos(angle)-self.x*math.sin(angle)
        )
    def rot90(self,turns):
        x=self.x
        y=self.y
        for _ in range(turns):
            temp=-x
            x=y
            y=temp
        return vector(x,y)
    def all90(self):
        x=self.x
        y=self.y
        full=[]
        for _ in range(4):
            temp=-x
            x=y
            y=temp
            full.append(vector(x,y))
        return full
    
    def intcoords(self):
        return int(self.x), int(self.y)
class shape:
    def __init__(self,position:vector,*args:vector) -> None:
        self.pos=position
        self.points=[]
        for vector in args:
            self.points.append(vector)
