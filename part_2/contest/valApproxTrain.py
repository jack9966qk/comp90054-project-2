from tqdm import tqdm
import imp
import numpy as np
import matplotlib.pyplot as plt
import cPickle

from rlGenerators import *
import itertools
from sklearn.metrics import mean_absolute_error

imp.load_source("player0", "baselineTeam.py")
imp.load_source("player1", "baselineTeam.py")

testInstances = list(addLabels(
    addFeatures(
        replayDataGenerator("/Users/Jack/Desktop/baseline-baseline/test/")
    )
))

X_test = np.array([f for _, _, _, f, _, _ in testInstances])
y_test = np.array([v for _, _, _, _, _, v in testInstances])

# print(X_test.shape)
# print(y_test.shape)
# print(X_test)
# print(y_test)


replayData = replayDataGenerator("/Users/Jack/Desktop/baseline-baseline/")
replayDataWithFeat = addFeatures(replayData)
instances = addLabels(replayDataWithFeat)

from sklearn.linear_model import SGDRegressor
model = SGDRegressor()

# from sklearn.linear_model import Ridge
# model = Ridge()

# model.partial_fit(X_test, y_test)
# print(model.predict(X_test))

def train(instances, model):
    i = 0
    finish = False
    while not finish:
        l = []
        for _ in range(5000):
            try:
                l.append(next(instances))
            except StopIteration:
                finish = True
                break
        X = np.array([f for _, _, _, f, _, _ in l])
        y = np.array([v for _, _, _, _, _, v in l])
        model.partial_fit(X, y)
        i += len(l)

        y_predict = model.predict(X)
        # print(y_predict)
        y_test_predict = model.predict(X_test)

        print("fitted {} instances, train error: {:.4f}, test error: {:.4f}".format(
            i, mean_absolute_error(y, y_predict), mean_absolute_error(y_test, y_test_predict)
        ))
        if i % 50000 == 0:
            print("save model")
            with open("valApproxModel/valApproxModel_{}.cpickle".format(i), "w") as f:
                cPickle.dump(model, f)

train(instances, model)