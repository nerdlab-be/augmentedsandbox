from matplotlib import pyplot as plt
import matplotlib.image as mpimg
import pickle as pcl 
from scipy.ndimage import gaussian_filter as gaussf
import numpy as np

import sandbox.geo.mapfeatures as mapfeatures

class Europe:
  def __init__(self, file_name, filter_param, box_shape, resolution):
    '''
    Europe constructor

    Parameters:
    file_name [string]: the name of the file containing the binary map of Europe (.np)
    filter_param [int]: the parameter influencing the blurring effect of the Gaussian filter
    box_shape [tuple of two ints]: number of squares in (x,y) direction
    resolution [int]: the resolution of one box in km
    '''
    self.file_name = file_name
    self.filter_param = filter_param
    print('Wait.. Reading map  of Europe.')
    self.data = self.read_map()
    self.box_shape = box_shape[0], box_shape[1]
    self.resolution = resolution # in km
    print('Wait.. Europe map is being processed. This can take several seconds.')
    self.R, self.theta = self.vector_analysis()
    self.tuple_eur = (self.R, self.theta)
    print('Europe map is processed.')

  def read_map(self):
    '''read image from binary file, called file_name, and filter with gaussian filter with filter_param'''
    # Open binary file and read the data
    try:
      with open(self.file_name, 'rb') as f:
        img = pcl.load(f)
    except(IOError,IndexError,EOFError):
      print('Could not read map..')
    
    # Blur image to remove small features with Gaussian filter
    return gaussf(img, sigma = self.filter_param)

  def vector_analysis(self):
    '''Loop through the map of Europe to analyse the subdata set'''
    # Unpack box_shape in x, y variables
    x, y = self.data.shape
    x_step, y_step = tuple(self.resolution * bs for bs in self.box_shape)

    # Initialize outputs
    R = []
    theta = []

    # Run through the data in blocks of resolution*i_step
    for i in range(0, x - x_step, self.resolution):
      for j in range(0, y - y_step, self.resolution):
          # Create a partition of the data that needs to be analyzed
          data_partition = self.data[i:i + x_step, j:j + y_step]
          R_temp, theta_temp = mapfeatures.process_window(data_partition, self.box_shape)
          R.append(R_temp)
          theta.append(theta_temp)
    return R, theta

  def save_data(self, file_name):
    '''Save the self.R and self.theta vectors in a file'''
    # Save the R vector
    with open(file_name + '_R', 'wb') as f:
      pcl.dump(self.R, f)
    
    # Save the theta vector
    with open(file_name + '_theta', 'wb') as f:
      pcl.dump(self.theta, f)

    
if __name__ == '__main__':
  eur = Europe('height.np', 50, [3, 4], 25)
  # print(len(eur.R))