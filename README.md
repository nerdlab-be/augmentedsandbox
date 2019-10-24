# augmentedsandbox

## Initial setup

1. Install Python 3.7
1. Clone this repository in home directory
1. `cd` into `augmentedsandbox`
1. `virtualenv --python=python3.7 env`
1. `env/bin/pip install -r requirements.txt`
1. from `sarndbox/Vrui-4.5-004`, run `make`
1. from `sarndbox/Kinect-3.6`, run `make` 
1. from `sarndbox/SARndbox-2.5`, run `make`


## Files
* **readGeoTiff.m**: To calculate the fft's of Europe.
* **mapEurope.m**: Calculates two parameters: the amount of water and the mountain rate.
