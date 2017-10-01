from collections import defaultdict
from capture import SCARED_TIME
from moreUtil import getHomeArea

class AdditionalState(object):
    def __init__(self, isRed, teamIndices):
        self.isRed = isRed
        self.teamIndices = teamIndices
        self.carry = {}
        for idx in self.teamIndices:
            self.carry[idx] = 0
        self.lastScaredTime = defaultdict(lambda: None)
    
    def update(self, gameState, agentIndex, action):
        newState = gameState.generateSuccessor(agentIndex, action)
        x, y = newState.getAgentPosition(agentIndex)
        food = gameState.getBlueFood() if self.isRed else gameState.getRedFood()
        capsule = gameState.getBlueCapsules() if self.isRed else gameState.getRedCapsules()
        opponents = gameState.getBlueTeamIndices() if self.isRed \
                    else gameState.getRedTeamIndices()
        if food[x][y]:
            self.carry[agentIndex] += 1
        if (x, y) in capsule:
            for idx in opponents:
                self.lastScaredTime[idx] = gameState.data.timeleft
        for idx in opponents:
            pos = gameState.getAgentPosition(idx)
            if pos == (x, y):
                self.lastScaredTime[idx] = None
        
        xLo, xHi = getHomeArea(gameState, self.isRed)
        if xLo <= x <= xHi:
            self.carry[agentIndex] = 0
    
    def isScared(self, gameState, opponentIdx):
        if not self.lastScaredTime[opponentIdx]: return False
        timeleft = gameState.data.timeleft
        return self.lastScaredTime[opponentIdx] - timeleft <= SCARED_TIME