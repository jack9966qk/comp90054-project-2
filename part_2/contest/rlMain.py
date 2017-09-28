import pickle

WEIGHT_FILENAME = "rlWeights.pickle"

def simulateGame(redTeam, blueTeam, weight):
    pass

# weight = ...
# redTeam = ...
# blueTeam = ...
rawData = simulateGame(redTeam, blueTeam, weight)
labels = getLabels(rawData)
features = extractFeatures(rawData)
weight = train(features, labels)
with open(WEIGHT_FILENAME, 'w') as f:
    pickle.dump(weight, f)
