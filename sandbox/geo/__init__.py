import os
from typing import Tuple, List
import pickle

import rasterio.warp
import rasterio.crs
import rasterio.transform
import numpy as np
from scipy import signal

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
        # with open(self._processed_height_path, 'rb') as f:
        #     self._processed_height_data = pickle.load(f).transpose()
        print('Processing data')
        print(self._raw_height_data.shape)
        self._processed_height_data = self._get_processed_height_values(self._raw_height_data, 327, 283)
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
        height_values = self._get_processed_height_values(image)
        corr = signal.correlate2d(self._processed_height_data, height_values, boundary='symm', mode='same')
        print("corr", corr)
        y, x = np.unravel_index(np.argmax(corr), corr.shape)
        print("xy", x, y)
        return x, y

    def _get_processed_height_values(self, image:np.ndarray, h=None, v=None) -> np.ndarray:
        values = []
        for vertical_strip in np.array_split(image, h or self._horizontal_segment_count):
            for segment in np.array_split(vertical_strip, v or self._vertical_segment_count, axis=1):
                max_height = np.max(segment)
                min_height = np.min(segment)
                segment = segment.astype(np.float64)
                height_range = max_height - min_height
                # print(depth_range)
                if height_range != 0:
                    normalized_segment = (segment - min_height) / height_range
                else:
                    normalized_segment = segment
                values.append(np.percentile(normalized_segment, 90) - np.percentile(normalized_segment, 10))
        arr = np.asarray(values)
        shape = (h or self._horizontal_segment_count, v or self._vertical_segment_count)
        return np.reshape(arr, shape)