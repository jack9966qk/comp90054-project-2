import sys
import util
import featuresTool
import numpy as np
import IOutil
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.neural_network import MLPClassifier
alpha = 0.1 # learning rate

HPFileName = "Hyper.json"
modelName = "modle.pickle"

# def extractFeatures(state, action, nextState, agent,featureTool):
#     # return features of state
#     temp = featureTool.getFeatures(agent,state,action,nextState)
#     res = [temp[line] for line in featureTool.dict]
#     return temp
#     pass


def extractFeatures(states, actions, agents):
    """
    Extract features of a game for all agents
    states - list of states of that agent in the game,
             states[0] is the initial state,
             states[-4:] are the outcomes (each being one of "Win", "Lose", "Tie")
    actions - list of actions the agent performed at each corresponding state
              actions[-1] = None
    agents - list of agent for each corresponding state
    return - list of features corresponding to each given state
    """
    atool = []
    
    atool.append(featuresTool.featuresTool())
    atool.append(featuresTool.featuresTool())
    for i in range(states[0].getNumAgents()):
        if states[0].isOnRedTeam(agents[i].index):
            atool[0].initGame(agents[i],states[i])
        else:
            atool[1].initGame(agents[i],states[i])
    
    features = []
    mods = []
   
    for i in range(len(states)):
        if not type(states[i]) == str:
            if states[i].isOnRedTeam(agents[i].index):
                tool = atool[0]
            else:
                tool = atool[1]
        else:
            tool = atool[0]
        #features.append(tool.getTrainSet(agents[i],states[i],actions[i],None))
        fea,mod = tool.getModSet(agents[i],states[i],actions[i],None)
        features.append(fea)
        mods.append(mod)
   

        
    #features.append([0])
    #print features,mods
    return features,mods
    
    pass

# def extractFeatures(agent, states, actions):
#     """
#     Extract features of a game for a agent
#     agent - CaptureAgent object
#     states - list of states of that agent in the game,
#              states[0] is the initial state,
#              states[-1] is the outcome (one of "Win", "Lose", "Tie")
#     actions - list of actions the agent performed at each corresponding state
#               actions[-1] = None
#     return - list of features corresponding to each given state
#     """
#     #print states
    
#     tool = featuresTool.featuresTool()
#     tool.initGame(agent,states[0])
    
#     features = []
#     mods = []
    
#     for i in range(len(states)-1):
#         tfea,tmod = tool.getModSet(agent,states[i],actions[i],None)
#         #features.append(tool.getTrainSet(agent,states[i],actions[i],None))
#         features.append(tfea)
#         mods.append(tmod)
        
#     features.append([0])
    
#     return features,mods

def train(features, actions, labels, model = "Linear"):
    # return trained weights
    if model == "Linear":
        return trainLinear(features, labels)
    
    if model == "MLP":
        return trainMLP(features, labels)
    
    if model == "MLPC":
        return trainMLPC(features, labels)
        
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
    model = MLPRegressor([15,10,10,10,10,5,5,5,5,5,5,3],max_iter=1000)
    model.fit(features,labels)
    
    IOutil.savePickle(modelName,model)


    return 0
    
    
def trainMLPC(features, labels):
    model = MLPClassifier([15,10,10,5,5,3],max_iter=1000)
    model.fit(features,labels)
    
    IOutil.savePickle(modelName,model)
    
    plabels = model.predict(features)
    
    #for i in range(len(labels)):
    #    print (labels[i],plabels[i])
    

    return 0
    
def times(a,b):
    temp = 0
    for i in range(len(a)):
        temp+=a[i]*b[i]
    return temp
    
    
    