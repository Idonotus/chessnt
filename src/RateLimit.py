import time
class RateLimitObj:
    def __init__(self,limit=180,refresh=60,timeout=0) -> None:
        self.limit=limit
        self.occurrences=0
        self.refreshtime=refresh
        self.timeout=timeout
        self.lastrefresh=time.time()
    
    def comapplicable(self,com):
        
        ...

        return True

    def refresh(self):
        self.occurrences=0

    def run(self,com):
        if not self.comapplicable(com):
            return None
        if time.time()-self.lastrefresh>=self.refreshtime:
            self.refresh()
        if self.occurrences>=self.limit:
            #deny
            ...
            return True
        self.occurrences+=1
        return False
        
        
        
class UserRateLimiter:
    def __init__(self,user,server) -> None:
        self.ratelimits={}
        self.server=server
        self.ratelimits["general"]=RateLimitObj()

    def run(self,com):
        if self.ratelimits["general"].run(com):
            self.server.leaveClient(self.user)