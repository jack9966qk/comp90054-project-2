def getLayoutSize(gameState):
  width = gameState.data.layout.width
  height = gameState.data.layout.height
  return width, height

def getHomeArea(gameState, isRed):
  width, height = getLayoutSize(gameState)
  return (0, width/2) if isRed else (width/2, width)