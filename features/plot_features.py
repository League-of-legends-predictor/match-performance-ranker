import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
print("Reading Data")
data = pd.read_csv("features/overall_samples.txt", sep=',', header=0)

col1 = data.columns.tolist()
column_length = len(col1)
print (column_length)

# Organise Data
print("Organising Data")
X = []
for i in range(0, column_length):
    Xi = data.iloc[:, i]
    X.append(Xi)
X = np.column_stack((X))
Y = data.iloc[:, -1]


titles = [
        # 'position [0]',
        'minutes [1]', 
        'op_score [2]', 'op_score/min [3]',
        'kill_participation [4]', 
        'kills [5]','kills/min [6]', 
        'deaths [7]','deaths/min [8]', 
        'assists [9]','assists/min [10]', 
        'takedowns [11]','takedowns/min [12]',
        'kpd [13]','kpd/min [14]', 
        'apd [15]','apd/min [16]',
        'tpd [17]','tpd/min [18]',
        'dmg_done [19]','dmg_done/min [20]',
        'dmg_taken [21]','dmg_taken/min [22]',
        'dmg_surplus [23]','dmg_surplus/min [24]',
        'dtr [25]','dtr/min [26]',
        'cw [27]','cw/min [28]',
        'wp [29]','wp/min [30]',
        'wk [31]','wk/min [32]',
        'ward_advantage [33]','ward_advantage/min [34]',
        'end_lvl [35]','end_lvl/min [36]', 
        'positive_impact [37]','positive_impact/min [38]',
]

from sklearn import preprocessing
ROWS =4
COLS =10
figure, axis = plt.subplots(ROWS,COLS)
for t,title in enumerate(titles):
    print(title)
    for tier in range(0,6):
        sum = 0
        count = 0
        # scaler = preprocessing.MinMaxScaler(feature_range=(0, 1))
        # normalizedlist=scaler.fit_transform(avg)
        for i,row in enumerate(X):
            if Y[i]==tier:
                sum+=row[t+1]
                count+=1
        avg = sum/count

        axis[t//COLS, t%COLS].set_title(title)
        axis[t//COLS, t%COLS].scatter(tier,avg, label=tier)

plt.legend()
plt.show()
