import numpy as np
import pandas as pd
from sklearn.model_selection import KFold, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, confusion_matrix

# ================================= Read Data =========================================================
print("Reading Data")
data = pd.read_csv("knn/knn_samples.txt", sep=',', header=None)

# Organise Data
print("Organising Data")
X = []
for i in range(0, 4):
    Xi = data.iloc[:, i]
    X.append(Xi)
X = np.column_stack((X))
Y = data.iloc[:, -1]
# ================================== TRAIN THE MODEL ========================================================
figure, axs = plt.subplots(1, 2)

# print cm of best model we found so far
print('Showing best so far')
best_model = KNeighborsClassifier(weights='uniform', n_neighbors=20, metric='minkowski')
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.20, random_state=101)
best_model.fit(X_train, y_train)
preds = best_model.predict(X_test)
cm = confusion_matrix(y_test, preds)
print(cm)

print(f'Tuning Hyper Params...')
# create ranges for hyper parameters
weight_types = ['uniform', 'distance']
Ks = [1, 25, 50, 100, 250, 500]
# pick the right samples
x = np.array(X)
y = np.array(Y)
# tune hyperparameters
for wi, wt in enumerate(weight_types):  # hyper param 1
    test_mean_acc = []
    test_std_acc = []
    train_mean_acc = []
    train_std_acc = []
    for k in Ks:  # hyper param 2
        test_temp = []
        train_temp = []
        knn = KNeighborsClassifier(
            weights=wt, n_neighbors=k, metric='minkowski')
        kf = KFold(n_splits=5, shuffle=True, random_state=69420)
        # perform cross validation
        for train, test in kf.split(x):
            knn.fit(x[train], y[train])
            test_y_pred = knn.predict(x[test])
            # get evaluate model performance
            acc = accuracy_score(y[test], test_y_pred)
            # save performance for plotting
            test_temp.append(acc)
            # repeat for training data to observe overfitting
            train_y_pred = knn.predict(x[train])
            acc = accuracy_score(y[train], train_y_pred)
            train_temp.append(acc)
        # get values for plotting the mean accuracy and std
        test_mean_acc.append(np.array(test_temp).mean())
        test_std_acc.append(np.array(test_temp).std())
        train_mean_acc.append(np.array(train_temp).mean())
        train_std_acc.append(np.array(train_temp).std())
    # plot the accuracy for the different values of the hyper param 2 in the column using hyper param 1
    axs[wi % 2].errorbar(Ks, test_mean_acc,
                            yerr=test_std_acc, label='test')
    axs[wi % 2].errorbar(Ks, train_mean_acc,
                            yerr=train_std_acc, label='train')
    axs[wi % 2].set_title(wt)
    axs[wi % 2].set(xlabel='K Value', ylabel='Accuracy')
plt.legend()    
plt.show()
  

