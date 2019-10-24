import numpy as np

def extrema(data):
  '''Get the extrema of an array or matrix
  
  Parameters:
  data: the data for which the extrema are searched

  Returns:
  tuple: minimum, maximum    
  '''
  min_val = np.amin(data)
  max_val = np.amax(data)
  return min_val, max_val

def extract_maximal_vector(data, global_extrema, size_per_box):
  '''From a box of data with size [resolution x resolution] the maximal vector size and angle is extracted'''
  # Find the local extrema of the data and its position
  local_min, local_max = extrema(data)
  min_coord = np.unravel_index(np.argmin(data), size_per_box)
  max_coord = np.unravel_index(np.argmax(data), size_per_box)

  # Check if the matrix is completly constant
  if (global_extrema[0] != global_extrema[1]):
    # Calculate the size of the maximal gradient vector
    vector_length = (local_max - local_min)/(global_extrema[1]-global_extrema[0])

    # Calculate the angle of the maximal gradient vector
    dy = max_coord[1] - min_coord[1]
    dx = max_coord[0] - min_coord[0]
    vector_angle = np.arctan2(dy, dx) # in rad
  else:
    vector_length = 0
    vector_angle = 0
  return vector_length, vector_angle

def process_window(data, box_shape):
  '''A partition of the data is analysed. A vector in each box of [resolution x resolution] a maximal vector is extracted.'''

  # Initialise the output vectors
  R = []
  theta = []

  # Retrieve global extrema of the data
  global_extrema = extrema(data)

  # Get and format size of data matrix
  x_size, y_size = data.shape
  x_step = x_size // box_shape[0]
  y_step = y_size // box_shape[1]
  size_per_box = (x_step, y_step)

  for i in range(0, box_shape[1]):
    for j in range(0, box_shape[0]):
      # Create a partition of the data with size resolution
      data_partition = data[j*x_step:(j + 1)*x_step, i*y_step:(i + 1)*y_step]

      # Extract maximal vector
      R_temp, theta_temp = extract_maximal_vector(data_partition, global_extrema, size_per_box)

      # add features to output vector
      R.append(R_temp)
      theta.append(theta_temp)

  return R, theta