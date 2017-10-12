def getReward(agent, gameState, prevState, terminal):
    if terminal:
        if agent.getScore(gameState) == 0:
            return -300
        else: return agent.getScore(gameState) * 500
    else:
        r = (agent.getScore(gameState) - agent.prevScore) * 30
        x, y = gameState.getAgentPosition(agent.index)
        if agent.getFood(prevState)[x][y]:
            # ate food
            r += 10
        if agent.prevIsIllegal:
            # had invalid action in last step
            r -= 25
        prevX, prevY = prevState.getAgentPosition(agent.index)
        if (abs(prevX - x) + (prevY - y)) > 1:
            # ate by opponent
            r -= 50

        enemies = [state.getAgentState(i) for i in prevState.getOpponents(gameState)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
        positions = [a.getPosition() for a in invaders]
        if len(positions) > 0 and not prevState.getAgentState(agent.index).isPacman:
            for position in positions:
                if (x, y) == position: r += 15 # chase invaders

        r -= 1 # time
        print("reward: {}".format(r))
        return r