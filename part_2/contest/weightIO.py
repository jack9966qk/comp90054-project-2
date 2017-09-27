import pickle

def saveWeights(weights, filename):
    with open(filename, "w") as f:
        pickle.dump(weights, f)

def loadWeights(filename):
    with open(filename) as f:
        return pickle.load(f)       