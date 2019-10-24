import os
from typing import Tuple, List
import pickle

import rasterio.warp
import rasterio.crs
import rasterio.transform
import numpy as np
from scipy import signal
from scipy.signal import sigtools
from scipy import misc

import random as rd
import matplotlib.pyplot as plt

import sandbox.data


data_dir = os.path.dirname(sandbox.data.__file__)
DEFAULT_HEIGHT_PATH = os.path.join(data_dir, 'height.tif')
DEFAULT_PROCESSED_HEIGHT_PATH = os.path.join(data_dir, 'processed-height.pkl')
DEFAULT_WATER_PATH = os.path.join(data_dir, 'water.tif')
WGS84 = rasterio.crs.CRS({'init': 'epsg:4326'})

# [v.shape for h in np.array_split(np.ones((9, 9)), 2) for v in np.array_split(h, 2, 1)]

class GeoData:

    def __init__(self,
            height_path:str=DEFAULT_HEIGHT_PATH,
            water_path:str=DEFAULT_WATER_PATH,
            processed_height_path:str=DEFAULT_PROCESSED_HEIGHT_PATH,
            horizontal_segment_count:int=4,
            vertical_segment_count:int=3):
        self._height_data = None
        self._raw_height_data = None
        self._processed_height_data = None
        self._water_data = None
        self._height_path = height_path
        self._processed_height_path = processed_height_path
        self._water_path = water_path
        self._horizontal_segment_count = horizontal_segment_count
        self._vertical_segment_count = vertical_segment_count
        self.load_data()

    def _load_tiff(self, path, raw_data_name):
        with rasterio.open(path) as data:
            setattr(self, raw_data_name, data.read(1).transpose())
            return data
    
    def load_data(self):
        self._height_data = self._load_tiff(self._height_path, '_raw_height_data')
        self._water_data = self._load_tiff(self._water_path, '_raw_water_data')
        with open(self._processed_height_path, 'rb') as f:
             self._processed_height_data = pickle.load(f).transpose()
        print('Processing data')
        print(self._processed_height_data)
        #self._processed_height_data = self._get_processed_height_values(self._raw_height_data, 327, 283)
        print('New processed data')
        print(self._processed_height_data)
        print('Done processing data')

    def pixels_to_coordinates(self, coords: Tuple[int, int]) -> Tuple[float, float]:
        x, y = coords
        src_x, src_y = rasterio.transform.xy(self._height_data.transform, y, x)
        xs, ys = rasterio.warp.transform(self._height_data.crs, WGS84, [src_x], [src_y])
        return xs[0], ys[0]

    @property
    def height(self):
        return self._raw_height_data
    
    @property
    def water(self):
        return self._water_data.data

    def find_best_match(self, image:np.ndarray) -> Tuple[int, int]:
        print('run best_match')
        height_values = self._get_processed_height_values(image)
        main_processed = np.mean(height_values)
        scale = 1.0
        height_values = np.random.rand(4, 3)
        print('New')
        print(scale*height_values)

        
        #corr = signal.correlate2d(self._processed_height_data, scale*height_values.transpose(), boundary='symm', mode='same')
        corr = self._own_correlate(self._processed_height_data, scale*height_values.transpose(), boundary='symm', mode='same')
        maxcorr = np.amax(corr)
        print("corr", np.amax(corr))
        for i in range(0, len(corr)):
            for j in range(0, len(corr[0])):
                if corr[i, j] == maxcorr:
                    x = i
                    y = j
        #y, x = np.unravel_index(np.argmax(corr, axis=None), corr.shape) 
        print("Highest Correlation",corr[x,y])
        
        #x = rd.randint(0,200)
        #y = rd.randint(0,200)

        print(self._processed_height_data[x:x+4, y:y+3])
        print("xy", x, y)
        return x, y

    def _own_correlate(self, Europa_map, Sandbox_data, mode='full', boundary='fill', fillvalue=0) -> Tuple[int, int]:
        in1 = np.asarray(Europa_map)
        in2 = np.asarray(Sandbox_data)

        if not in1.ndim == in2.ndim == 2:
            raise ValueError('_own_correlate inputs must both be 2D arrays')

        swapped_inputs = True #np._inputs_swap_needed(mode, in1.shape, in2.shape)
        if swapped_inputs:
            in1, in2 = in2, in1

        #val = _valfrommode(mode)
        #bval = _bvalfromboundary(boundary)
        out = sigtools._convolve2d(in1, in2.conj(), 0)

        if swapped_inputs:
            out = out[::-1, ::-1]

        ascent = misc.ascent()
        fig, (ax_orig, ax_mag, ax_ang) = plt.subplots(3, 1, figsize=(6, 15))
        ax_orig.imshow(ascent, cmap='gray')
        ax_orig.set_title('Original')
        ax_orig.set_axis_off()
        ax_mag.imshow(np.absolute(out), cmap='gray')
        ax_mag.set_title('Gradient magnitude')
        ax_mag.set_axis_off()
        ax_ang.imshow(np.angle(out), cmap='hsv') # hsv is cyclic, like angles
        ax_ang.set_title('Gradient orientation')
        ax_ang.set_axis_off()
        fig.show()

        return out


    def _get_processed_height_values(self, image:np.ndarray, h=None, v=None) -> np.ndarray:
        values = []
        flag_image = True
        #print(image)
        #print('Image size: ')
        #print(len(image))
        #print(len(image[0]))
        for vertical_strip in np.array_split(image, h or self._horizontal_segment_count):
            for segment in np.array_split(vertical_strip, v or self._vertical_segment_count, axis=1):
                if (len(segment)>20) & (len(segment[0])>20):
                    
                    #print(len(segment))
                    #print(len(segment[0]))
                    max_height = np.max(segment)
                    min_height = np.min(segment)
                    segment = segment.astype(np.float64)
                    height_range = max_height - min_height
                    # print(height_range)
                    if height_range != 0:
                        normalized_segment = (segment - min_height) / height_range
                    else:
                        normalized_segment = segment
                    values.append(np.percentile(normalized_segment, 90) - np.percentile(normalized_segment, 10))
                else:
                    values.append(0)
                    flag_image = False
        
        if flag_image:
            arr = np.asarray(values)
            shape = (h or self._horizontal_segment_count, v or self._vertical_segment_count)
            return np.reshape(arr, shape)
        else:
            return [-1]
