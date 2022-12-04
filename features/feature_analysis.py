from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

# Read Data
print("Reading Data")
data = pd.read_csv("overall_samples.txt", sep=',')
print("Organising Data")
X = []
for i in range(0,40):
    Xi = data.iloc[:,i]
    X.append(Xi)
X = np.column_stack((X))
Y = data.iloc[:, -1]

titles = [ 
'min [1]', 'op score [2]', 'kill participation [3]', 'k/m [4]',
' d/m [5]',' a/m [6]','t/m [7]',' k/d [8]',' a/d [9]', 
't/d [10]',' (k/d)/m [11]',' (a/d)/m [12]',' (t/d)/m [13]',
' dd [14]',' dd/m [15]',' dt [16]',' dt/m [17]',' d/t [18]',
' (d/t)/m [19]','t/d [20]', '(t/d)/m [21]',' cw/m [22]',
' wp/m [23]',' wk/m [24]',' lvl/m [25]',' val/m [26]',
  'absolute_damage_per_min[27]',
    'absolute_kd_per_min[28]',
    'overall_contribution[29]',
    'cw_min_sqr[30]',
    'wp_min_sqr[31]',
    'fury[32]',
    'backbone_value[33]',
    'relative_contribution[34]',
    'relative_damage[35]',
    'relative_value[36]',

]
print('Making plots...')
figure, axis = plt.subplots(4,9)
for t,title in enumerate(titles):
    print(title)
    axis[t//9, t%9].set_title(title)
    for tier in range(0,6):
        sum = 0
        count = 0
        for i,row in enumerate(X):
            if Y[i]==tier:
                sum+=row[t+1]
                count+=1
        avg = sum/count
        axis[t//9, t%9].scatter(tier,avg, label=tier)

plt.scatter(X[:,27],Y)
plt.legend()
plt.show()

