

class tool():
    
    def initGame(self,agent,gameState):
        #if not agent.index == agent.getTeam(gameState)[0]: return
        
        self.walls = gameState.getWalls()
        self.size = (self.walls.width,self.walls.height)
        self.allpos = [(i,j) for i in range(self.size[0]) for j in range(self.size[1]) if not self.walls[i][j]]
        self.probMap = [[gameState.getInitialAgentPosition(i)] for i in range(gameState.getNumAgents())]
        self.start = gameState.getAgentPosition(agent.index)[0]
        self.middle = (self.size[0]/2) - (self.start%2)
        self.team = agent.getTeam(gameState)
        self.mate = [i for i in self.team if not i ==agent.index]
        self.opp = agent.getOpponents(gameState)
        self.teamNum = gameState.getNumAgents()
        self.lastidx = 0
        self.lastpos = None
        self.lastState = [gameState for i in range(self.teamNum)]
        self.lastpos = [gameState.getAgentPosition(agent.index) for i in range(self.teamNum)]
        self.lastCapsules = len(agent.getCapsules(gameState))
        self.scareTimeLeft = 0
       # print self.allpos
        return