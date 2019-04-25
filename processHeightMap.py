import pickle
import matplotlib.pyplot as plt
import numpy as np
import math
from PIL import Image

with open('mountainEurope15_15.pkl', 'rb') as fin : 
    mountain = pickle.load(fin)
    
with open('waterEurope15_15.pkl', 'rb') as fin :
    water = pickle.load(fin)
   

#X = np.arange(0, 327, 1)
#Y = np.arange(0, 284, 1)
#X, Y = np.meshgrid(X, Y)
#water;
#
#fig = plt.figure()
#ax1 = fig.add_subplot(121, projection='3d')
#ax2 = fig.add_subplot(122, projection='3d')
#ax1.plot_surface(X, Y, mountain,cmap=cm.coolwarm,
#                       linewidth=0, antialiased=False)
#ax2.plot_surface(X, Y, water,cmap=cm.coolwarm,
#                       linewidth=0, antialiased=False)
#plt.show()


pic = Image.open("height.png")
HeigthMap = np.array(pic)

    
sizeMountain = np.shape(mountain)
sizeHM = np.shape(HeigthMap)
divisions = (3, 4)
divisionsPixel = np.divide(sizeHM, divisions)
mountainHM = []

    
for i in range(0, sizeHM[0], math.floor(divisionsPixel[0])):
    for j in range(0, sizeHM[1], math.floor(divisionsPixel[1])):
        print(i)
        print(j)
        partialHeightMap = HeigthMap[i:i+divisionsPixel[0], j:j+divisionsPixel[1]]
        mountain_temp = np.percentile(partialHeightMap, 90) - np.percentile(partialHeightMap, 10)
        mountainHM.append(mountain_temp)
        
for i in range(0, sizeMountain[0]):
    for j in range(0, sizeMountain[1]):
        maskedMtn = mountain[i:i+divisions[0],j:j+divisions[1]]
        maskedInvMtn = np.flip(maskedMtn,1)
        