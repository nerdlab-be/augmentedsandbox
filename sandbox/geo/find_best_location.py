from .europe import Europe
import sandbox.geo.mapfeatures as mapfeatures

import struct
import numpy as np
import matplotlib.pyplot as plt

class FindBestLocation():
  def __init__(self, file_name, filter_param, box_shape, resolution):
      """
      Find_best_location constructor

      Parameters:
      filter_param: the parameter influencing the blurring effect of the Gaussian filter
      filter_param [int]: the parameter influencing the blurring effect of the Gaussian filter
      box_shape [tuple of two ints]: number of squares in (x,y) direction
      resolution [int]: the resolution of one box in km
      """

      self.europe = Europe(file_name, filter_param, box_shape, resolution)
      self.current_sandbox = []
      self.sandbox_size = None
      self.box_shape = box_shape

  def get_coordinates(self, new_map) -> tuple:
    """
    Process sandbox data

    Parameters:
      new_map: [numpy 2D array ] the map of the current sandbox
    """
      
    # self.current_sandbox = new_map
    self.sandbox_size = np.shape(new_map)

    # Invert sandbox data: point furthest away is the lowest point and vice versa
    current_sandbox_min = np.amin(new_map)
    current_sandbox_max = np.amax(new_map)
    self.current_sandbox = (-1)*new_map + current_sandbox_max + current_sandbox_min

    # Process the sandbox data to obtain an array with R and theta from sandbox
    tuple_sb = self.process_sandbox(self.current_sandbox)

    # Correlate the (R, theta) tuple of europe with sandbox
    return self.correlate_sandbox(tuple_sb, self.europe.tuple_eur)

  def process_sandbox(self, data):
    """
    The sandbox is subdivided in self.box_shape boxes and each box is analysed. An R and theta array is returned.

    Parameters:
    data [2D Matrix numpy]: the full current sandbox data
    """
    return mapfeatures.process_window(data, self.box_shape)

  def correlate_sandbox(self, tuple_sb, tuple_eur, plot=False) -> tuple:
    """Looks for the best match between the tuple of the sandbox and all Europe tuples.
    
    Parameters:
      :tuple_sb: the tuple of R and theta values of the sandbox.
      :tuple_eur: the tuple containing the R and theta vector of the europe map.
      :plot: Boolean to indicate if you want some visuals (Default: False).
    """
    # Initialize parameters with extreme values
    cost_best = 10000
    position_best = -1

    # Initialize solution vector
    if plot:
      cost_all = []

    # Extract parameters from tuple
    R_sb, theta_sb = tuple_sb
    R_eur, theta_eur = tuple_eur

    # Run trough tuple of europe and do an analysis with the sandbox parameters
    for i in range(0, len(R_eur)):
      # Calculate the minimized vector substraction
      cost = self.vector_substraction(theta_eur[i], R_eur[i], theta_sb, R_sb)

      # If the visuals are on, the cost per pixel is saved.
      if plot:
        cost_all.append(cost)
        
      # Check if the cost improved. If yes, this is new solution.
      if (cost_best > cost):
        cost_best = cost
        position_best = i

    # Obtain the shape tuple of Europe taking into account the resolution
    x_size_europe, y_size_europe = self.europe.data.shape
    shape = (x_size_europe // self.europe.resolution, y_size_europe // self.europe.resolution)

    # Find the best position
    best_pos_shaped = np.unravel_index(position_best, shape)

    # Plot visuals
    if plot:
      plt.imshow(np.reshape(cost_all, (shape[0] - self.box_shape[0] + 1, shape[1] - self.box_shape[1] + 1)))
      plt.show()

    return best_pos_shaped

  def vector_substraction(self, th_eur, r_eur, th_sb, r_sb):
    """
    The minimal distance between a bunch of vectors is searched.

    Parameters:
      :th_eur: the vector of angles for one fraction of Europe with size box_shape.
      :r_eur: the vector sizes for one fraction of Europe with size box_shape.
      :th_sb: the angles of the sandbox.
      :r_sb: the size of the sandbox.
    """
    # Initialize the cost vector
    cost = []
    
    # Loop through the fraction of europe and calculate the vector cost
    for i in range(1, len(r_eur)):
      # Check if the location is just sea and nothing else. Do not take this position.
      if (np.sum(r_eur) == 0):
        cost.append(20)
      else:
        (x1, y1) = (np.cos(th_eur[i])*r_eur[i], np.sin(th_eur[i])*r_eur[i])
        (x2, y2) = (np.cos(th_sb[i])*r_sb[i], np.sin(th_sb[i])*r_sb[i])
        cost.append(np.sqrt(((y2 - y1)**2 + (x2 - x1)**2)))

    # Make the cost function nonlinear. Favour very good single vectors.
    mask = len([c for c in cost if c > 1])
    cost_sum = sum(el**4 for el in cost)
    if (mask > 2):
      cost_sum +=  10
      
    return cost_sum


if __name__ == '__main__':
  fbl = FindBestLocation('height.np', 50, [3, 4], 25)
  
  with open('height-montblanc.dat', mode="rb") as fn:
    data = struct.unpack('f'*307200, fn.read(1228800))

  ls = list(data)
  arr = np.asarray(ls)

  # resize
  x_size = 480
  y_size = 640
  shape = (x_size, y_size)
  matrix = np.reshape(arr, shape)
  matrix = matrix[60:-50, 60:-80]
  # print(fbl.get_coordinates(matrix))