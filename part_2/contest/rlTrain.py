import sys
import util
import featuresTool
import numpy as np
import IOutil
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
alpha = 0.1 # learning rate

HPFileName = "Hyper.json"
modelName = "modle.pickle"

# def extractFeatures(state, action, nextState, agent,featureTool):
#     # return features of state
#     temp = featureTool.getFeatures(agent,state,action,nextState)
#     res = [temp[line] for line in featureTool.dict]
#     return temp
#     pass

def extractFeatures(agent, states, actions):
    """
    Extract features of a game for a agent
    agent - CaptureAgent object
    states - list of states of that agent in the game,
             states[0] is the initial state,
             states[-1] is the outcome (one of "Win", "Lose", "Tie")
    actions - list of actions the agent performed at each corresponding state
              actions[-1] = None
    return - list of features corresponding to each given state
    """
    #print states
    
    tool = featuresTool.featuresTool()
    tool.initGame(agent,states[0])
    
    features = []
    mods = []
    
    for i in range(len(states)-1):
        tfea,tmod = tool.getModSet(agent,states[i],actions[i],None)
        #features.append(tool.getTrainSet(agent,states[i],actions[i],None))
        features.append(tfea)
        mods.append(tmod)
        
    features.append([0])
    
    return features,mods

def train(features, actions, labels, model = "Linear"):
    # return trained weights
    if model == "Linear":
        return trainLinear(features, labels)
    
    if model == "MLP":
        return trainMLP(features, labels)
        
        
    print "Undefined model"
    sys.exit(1)

def trainLinear(features, labels):
    '''
    # initialize weights
    weights = [0.1 for i in range(len(features[0]))]
    # stochastic gradient descent
    #print len(labels
    for i in range(len(labels)):
        feature = features[i]
        diff = labels[i] - times(feature,weights)#features[i] * weights
        for j in range(len(feature)):
            weights[j] += alpha * diff * feature[j]
       # for feature, value in features[i].iteritems():
       #     weights[feature] += alpha * diff * value
        print weights
        util.pause()
    '''
    '''
    afeatures = np.array(features)
    alabels = np.array(labels)
    
    linreg = LinearRegression()

    linreg.fit(afeatures, alabels)
    
    weights = linreg.coef_
    print weights
    '''
    afeatures = np.array(features)
    alabels = np.array(labels)
    
    model = LinearRegression()
    model.fit(afeatures,alabels)
    
    IOutil.savePickle(modelName,model)
    weights = model.coef_
    
    #return 0
    return np.ndarray.tolist(weights)
    
def trainMLP(features, labels):
    model = MLPRegressor([8,5,5,5,5,5,5,5,3],max_iter=500)
    model.fit(features,labels)
    
    IOutil.savePickle(modelName,model)


    return 0
    
def times(a,b):
    temp = 0
    for i in range(len(a)):
        temp+=a[i]*b[i]
    return temp
    
    
    