import sys
import util

alpha = 0.1 # learning rate

def extractFeatures(state, action, nextState, agent,featureTool):
    # return features of state
    temp = featureTool.getFeatures(agent,state,action,nextState)
    res = [temp[line] for line in featureTool.dict]
    return temp
    pass

def train(features, actions, labels, model):
    # return trained weights
    if model == "Linear":
        return trainLinear(features, labels)
    else:
        print "Undefined model"
        sys.exit(1)

def trainLinear(features, labels):
    # initialize weights
    weights = util.Counter()
    # stochastic gradient descent
    for i in len(labels):
        diff = labels[i] - features[i] * weights
        for feature, value in features[i].iteritems():
            weights[feature] += alpha * diff * value
    return weights