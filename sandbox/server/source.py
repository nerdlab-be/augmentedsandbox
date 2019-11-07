import struct
import sys
import os

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import numpy as np


class HeightSource(FileSystemEventHandler):

    def __init__(self, filename='height.dat'):
        self._filename = filename
        self._callbacks = []
        self._heightmap = self._load_heightmap()

    def on_update(self, callback):
        self._callbacks.append(callback)
        return callback

    def _load_heightmap(self) -> np.matrix:
        with open(self._filename, mode="rb") as f:
            data = struct.unpack('f'*307200, f.read(32*307200))
        #Convert to matrix
        x_size = 480
        y_size = 640
        lst = list(data)
        arr = np.asarray(lst)
        shape = (x_size, y_size)
        matrix = np.reshape(arr, shape)
        x_resize = x_size
        y_resize = y_size
        matrix_resize = matrix[0:x_resize, 0: y_resize]
        return matrix_resize

    def on_modified(self, event):
        if os.path.basename(self._filename) in event.src_path:
            print('Loading heightmap', file=sys.stderr)
            self._heightmap = self._load_heightmap()
            for callback in self._callbacks:
                callback(self._heightmap)

    def run(self):
        observer = Observer()
        observer.schedule(self, '.', recursive=True)
        observer.start()

    @property
    def heightmap(self) -> np.matrix:
        return self._heightmap
