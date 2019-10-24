## Jasper's Jolly Jewel: A short manual

* find_best_location.py:
    The main file. This file has to be run and contains a class that contains a processed Europe map. The class object has the function __get_coordinates()__ which accepts as an input a numpy matrix of the sandbox and returns the best match with the sandbox data.

* europe.py:
    The file contains a class object __Europe()__ that processes te file __height.np__. This file is a raw data matrix with the height profile of Europe.

* mapfeatures.py:
    This is a helper file that contains various definitions that are used in __find_best_location.py__ and __europe.py__.