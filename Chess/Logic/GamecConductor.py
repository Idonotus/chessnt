class Conductor:
    """Handles turn order and server communication"""
    def __init__(self,turnorder:list,servermode=False) -> None:
        self.turnorder=self.genturn(turnorder)
        self.servermode=servermode
    
    def genturn(self,turnorder):
        while True:
            t=turnorder[0]
            turnorder.pop(0)
            turnorder.append(t)
            yield t

    def newturn(self):
        if self.servermode:
            self.logic.teamturn=[-1]
            return
        
        self.logic.teamturn=[next(self.turnorder)]