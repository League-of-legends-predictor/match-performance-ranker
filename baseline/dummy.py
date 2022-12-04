import numpy as np
import pandas as pd
from sklearn.model_selection import KFold, train_test_split


# Read Data
print("Reading Data")
data = pd.read_csv("features/all_features.txt", sep=',', header=None)

# Organise Data
print("Organising Data")
X = []
for i in range(0, 27):
    Xi = data.iloc[:, i]
    X.append(Xi)
X = np.column_stack((X))
Y = data.iloc[:, -1]

# ============================== Split by role =========================================

Xs = [[], [], [], [], []]
Ys = [[], [], [], [], []]

for i, row in enumerate(X):
    Xs[int(row[0])].append(row)
    Ys[int(row[0])].append(Y[i])

# =============================================== Get 'Clean' Samples =======================================
# function to filter a dataset where the samples are within set std range
def filterBySTD(old_x, old_y, featureIndex):
    old_x = np.array(old_x)
    old_y = np.array(old_y)
    new_x = []
    new_y = []
    feature = old_x[:, featureIndex]
    std = np.array(feature).std()
    mean = np.array(feature).mean()
    for row, tier in zip(old_x, old_y):
        if (abs(mean - row[featureIndex]) <= std*1):
            new_x.append(row)
            new_y.append(tier)
    return new_x, new_y


for i, y in enumerate(Ys):
    tiers = [[[], []] for _ in range(6)]
    for j, tier in enumerate(y):
        tiers[tier][1].append(tier)
        tiers[tier][0].append(Xs[i][j])
    for tier in tiers:
        tier[0], tier[1] = filterBySTD(tier[0], tier[1], -2)
    new_x = tiers[0][0] + tiers[1][0] + tiers[2][0] + \
        tiers[3][0] + tiers[4][0] + tiers[5][0]
    new_y = tiers[0][1] + tiers[1][1] + tiers[2][1] + \
        tiers[3][1] + tiers[4][1] + tiers[5][1]
    Xs[i] = new_x
    Ys[i] = new_y
    print(len(new_x))

#================================== Concat All Samples =======================================================
concatx = []; concaty = []
for x in Xs:
    concatx = concatx + x
for y in Ys:
    concaty = concaty + y
# ================================== TRAIN THE MODELS ========================================================

from sklearn.dummy import DummyClassifier
X_train, X_test, y_train, y_test = train_test_split(concatx, concaty, test_size=0.20, random_state=101)
# create dummy classifier
dummy_clf = DummyClassifier(strategy='uniform', random_state=42)
# train a model
dummy_clf.fit(X_train, y_train)
y_pred = dummy_clf.predict(X_test)

# get accuracy score
print("the accuracy of the dummy model {}\n".format(dummy_clf.score(X_test, y_test)))
print("len xtest {}, len ypred {}".format(len(X_test),len(y_pred)))
