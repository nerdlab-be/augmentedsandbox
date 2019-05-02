from io import BytesIO
import json
import random

import numpy as np
from flask import Flask, send_file, Response, render_template
from PIL import Image

from sandbox.server.source import HeightSource
from sandbox.geo import GeoData

app = Flask(__name__)
source = HeightSource()
geo_data = GeoData()


def crop_matrix(m):
    return m[50:400, 100:-40]


@app.route("/height.<format>")
def height(format: str):
    cropped_matrix = crop_matrix(source.heightmap)
    max_depth = np.max(cropped_matrix)
    min_depth = np.min(cropped_matrix)
    depth_range = max_depth - min_depth

    # this always normalizes the heights to [0, 1], with the minimum value mapped to 0
    # and the maximum value mapped to 1. This makes a relatively flat terrain extremely
    # rugged, so this should change at some point.
    uint8_matrix = ((cropped_matrix - min_depth) / depth_range * 255).astype(np.uint8)
    
    if format in {'png', 'bmp'}:
        img_io = BytesIO()
        img = Image.fromarray(uint8_matrix, 'L')
        img.save(img_io, format)
        img_io.seek(0)
        return send_file(img_io, mimetype='image/' + format.lower())
    
    if format == 'raw':
        data = uint8_matrix.astype(np.uint16).tostring()
        return Response(data, mimetype='image/unity-raw')

    return 'invalid format'


@app.route('/coords/<int:x>/<int:y>')
def coords(x, y):
    return str(geo_data.pixels_to_coordinates((x, y)))


@app.route('/lol')
def lol():
    return json.dumps(geo_data._raw_height_data.shape)


@app.route('/map')
def map():
    return render_template('map.html.j2')


@app.route('/location')
def location():
    cropped_matrix = crop_matrix(source.heightmap)
    max_depth = np.max(cropped_matrix)
    min_depth = np.min(cropped_matrix)
    depth_range = max_depth - min_depth
    # this always normalizes the heights to [0, 1], with the minimum value mapped to 0
    # and the maximum value mapped to 1. This makes a relatively flat terrain extremely
    # rugged, so this should change at some point.
    normalized_matrix = (cropped_matrix - min_depth) / depth_range
    raw_x, raw_y = geo_data.find_best_match(normalized_matrix)
    return json.dumps(tuple(reversed(geo_data.pixels_to_coordinates((raw_x * 15, raw_y * 15)))))

source.run()
app.run("0.0.0.0", debug=True)
