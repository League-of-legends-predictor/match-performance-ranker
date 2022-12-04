from math import ceil
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import KFold, train_test_split
from sklearn.neighbors import KNeighborsClassifier

# Read Data
print("Reading Data")
data = pd.read_csv("random_forest/rf_samples.txt", sep=',', header=None)

# Organise Data
print("Organising Data")
X = []
for i in range(0, 11):
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
        if (abs(mean - row[featureIndex]) <= std/7):
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

#=================================== Train Model ============================================================
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(concatx, concaty, test_size=0.20, random_state=101)

from sklearn.ensemble       import RandomForestRegressor, RandomForestClassifier
print('Showing best so far')
model=RandomForestClassifier(bootstrap=True, max_depth=2980, max_features=None, min_samples_leaf=10, min_samples_split=0.001, n_estimators=12)
model.fit(X_train, y_train)
preds = model.predict(X_test)
cm = confusion_matrix(y_test, preds)
print(cm)
acc = model.score(X_test, y_test)
print(acc)


from sklearn.pipeline       import make_pipeline

import numpy as np
pipelines = {
    'rf':make_pipeline(RandomForestRegressor(random_state=1))
}

#========== The ideal range of values we would scan, but can't due to time limits ===============
n_samples = len(X_train)
# Number of trees in random forest
n_estimators = [int(x) for x in np.linspace(start = 10, stop = 1000, num = 10)]
# Maximum number of levels in tree
max_depth = [None, n_samples*0.1, n_samples*0.25, n_samples*0.5, n_samples*0.75]
# Minimum number of samples required to split a node
min_samples_split = [2,4,6,8,10]
# Minimum number of samples required at each leaf node
min_samples_leaf = [1, 10, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25]
# Number of features to consider at every split
max_features = [None, 'sqrt', 'log2',  1, 0.25, 0.5, 0.75]
# Method of selecting samples for training each tree
bootstrap = [True, False]

# we had to reduce the range of hyperparams to tune
grid = {
        'n_estimators': [12, 100],
        'max_depth': [None, ceil(n_samples*0.1), ceil(n_samples*0.25)],
        'min_samples_split': [2, 0.001, 0.005],
        'min_samples_leaf': [10, 50, 100],
        'max_features': [None],
        'bootstrap': [True],
}

from sklearn.model_selection    import GridSearchCV
model = RandomForestClassifier()
grid = GridSearchCV(
    estimator = model, 
    param_grid = grid,
    cv = KFold(n_splits=3, shuffle=True, random_state=101),
    verbose=2,
    n_jobs = -1,
    scoring='accuracy'
)
grid.fit(X_train, y_train)
print("The best parameters for Random forest were \n{}".format(grid.best_params_))
print("Training accuracy: {}\nTesting accuracy: {}".format(
    grid.score(X_train,y_train),
    grid.score(X_test,y_test)
    )
)
df = pd.DataFrame(grid.cv_results_)
df = df.sort_values(by='mean_test_score', ascending=False)
df.to_csv("grid_results.csv")

