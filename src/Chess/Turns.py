from typing import overload,Literal,Iterable
from .Piece.Logic import Piece

class Turn:
    def __init__(self,teams:list|str|int=[],pieces:list=[],piecemode:Literal["off","allow","deny"]="off"):
        if piecemode not in ["off","allow","deny"]:
            piecemode="off"
        self.piecemode="off"
        self.teams:set=set()
        self.pieces:set=set()
        self.setTeams(teams)
        self.setPieces(pieces)
        self.deactivatedteams:set=set()
        
    @overload
    def setPieces(self,pieces:str): ...
    @overload
    def setPieces(self,pieces:Iterable[str]): ...
    def setPieces(self,pieces:list[str]|str):
        if isinstance(pieces,str):
            self.pieces={pieces}
        elif isinstance(pieces,Iterable):
            self.pieces=set(pieces)
        else:
            raise TypeError

    @overload
    def setTeams(self,teams:Iterable[int]) -> None: ...
    @overload
    def setTeams(self,teams:str) -> None: ...
    @overload
    def setTeams(self,teams:int) -> None: ...
    def setTeams(self,teams:list|str|int=[]) -> None:
        if isinstance(teams,int):
            self.teams={teams}
        elif isinstance(teams,Iterable):
            self.teams=set(teams)
        elif isinstance(teams,str):
            if teams.isdigit():
                self.teams={int(teams)}
            else: raise ValueError
        else:
            raise TypeError
    
    def getActivity(self):
        return len(self.teams)>=0
    
    def deactivateTeam(self,team:int):
        if not team in self.teams:
            return
        self.deactivatedteams.add(team)
        self.teams.remove(team)
    
    def activateTeam(self,team:int):
        if not team in self.deactivatedteams:
            return
        self.deactivatedteams.remove(team)
        self.teams.add(team)

    def validatemove(self,selpiece:Piece):
        teams=selpiece.team
        if not ((isinstance(teams,int) and \
             teams in self.teams) or \
             (isinstance(teams,Iterable) and \
             self.teams.isdisjoint(teams))):
            return False
        if self.piecemode=="off":
            ...
        elif self.piecemode=="allow" and selpiece not in self.pieces:
            return False
        elif self.piecemode=="deny" and selpiece in self.pieces:
            return False
        return True

    def export(self):
        return {"teams":self.teams,"pieces":self.pieces,"piecemode":self.piecemode}

class TurnManager:
    def __init__(self,turnorder:Iterable) -> None:
        self.torder:list[Turn]=[]
        self.loadorder(turnorder)
    def loadorder(self,turnorder:Iterable):
        self.torder=[]
        for turn in turnorder:
            if isinstance(turn,dict):
                self.torder.append(Turn(**turn))
            elif isinstance(turn,(int,Iterable)):
                self.torder.append(Turn(teams=turn))
    def __iter__(self):
        return self

    def deactiveteam(self,teamid:int):
        for turn in self.torder:
            turn.deactivateTeam(teamid)

    def activeteam(self,teamid: int):
        for turn in self.torder:
            turn.activateTeam(teamid)
        
    def __next__(self):
        for i,turn in enumerate(self.torder):
            if turn.getActivity():
                self.torder=self.torder[i+1:len(self.torder)]+self.torder[0:i+1]
                return turn
        else:
            raise Exception("No applicable turns")
NULL_TURN=Turn(-1,piecemode="allow")