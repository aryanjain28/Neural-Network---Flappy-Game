import warnings
warnings.filterwarnings('ignore')

import tensorflow as tf
from tensorflow import keras
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

data = pd.read_csv('/home/aryan/Desktop/Flappy bird/generatedData.csv')



model = keras.models.load_model('/home/aryan/Desktop/Flappy bird/trainedModel.h5')

y = data['jump']
x = data[['topDistance','bottomDistance','birdPosition']]

v = []
for i in range(10, 20):
    v.append(x['topDistance'][i])
    v.append(x['bottomDistance'][i])
    v.append(x['birdPosition'][i])
    
    print(model.predict(np.array([v])), y[i])
    v.clear()

# print(x.head())

# xTrain, xTest, yTrain, yTest = train_test_split(x, y, test_size=0.1, shuffle=True)

# # # model
# model = keras.Sequential()
# model.add(keras.layers.Dense(6, input_dim=3, activation='relu'))   #layer 1
# model.add(keras.layers.Dense(4, activation='relu'))                     #layer 1
# model.add(keras.layers.Dense(1, activation='relu'))                     #layer 2
# model.add(keras.layers.Dense(1, activation='sigmoid'))                     #layer 3


# model.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy'])
# model.fit(xTrain, yTrain, epochs=20, shuffle=True)

# print(model.evaluate(xTest, yTest))

# model.save('trainedModel.h5')
# print('Model saved')




# model = keras.models.load_model('/home/aryan/Desktop/Flappy bird/trainedModel.h5')
# data = [468,231.70293481093415,205.2711621246394]

# prediction = model.predict(np.array([data]))

# print(prediction)

# if (prediction >= 0.5):
#     print('Jump')
# else:
#     print('Hold')