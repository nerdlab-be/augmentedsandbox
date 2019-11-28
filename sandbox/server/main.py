from io import BytesIO
import os
import json
import random
from enum import Enum
from typing import Dict, Any
import sys

import numpy as np
from flask import Flask, send_file, Response, render_template, request, send_from_directory
from PIL import Image
from random import randrange

from sandbox.server.source import HeightSource
from sandbox.geo import GeoData
from sandbox.geo.find_best_location import FindBestLocation

app = Flask(__name__)
source = HeightSource(sys.argv[1])
geo_data = GeoData()
default_options = dict(
    top=0,  # inclusive
    left=0,  # inclusive
    bottom=480,  # exclusive
    right=640,  # exclusive
    min_depth=-791.5076293945312,
    max_depth=-709.21630859375,
)
location_seeker = FindBestLocation('data/height.np', 50, [3, 4], 25)


def load_options() -> Dict[str, Any]:
    try:
        with open('config.json') as f:
            return json.load(f)
    except IOError:
        return default_options

options = load_options()


def update_options(updates: Dict[str, Any]) -> Dict[str, Any]:
    options.update(updates)
    with open('config.json', 'w') as f:
        json.dump(options, f)
    return options


def crop_matrix(m):
    return m[options["top"]:options["bottom"], options["left"]:options["right"]]


@app.route("/raw-normalized-height.png")
def raw_normalized_height():
    cropped_matrix = source.heightmap
    max_depth = np.max(cropped_matrix)
    min_depth = np.min(cropped_matrix)
    depth_range = max_depth - min_depth
    uint8_matrix = ((cropped_matrix - min_depth) / depth_range * 255).astype(np.uint8)
    img_io = BytesIO()
    img = Image.fromarray(uint8_matrix, 'L')
    img.save(img_io, 'png')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')
    

@app.route("/height.<format>")
def height(format: str):
    if request.args.get('cropped') == 'false':
        cropped_matrix = source.heightmap
    else:
        cropped_matrix = crop_matrix(source.heightmap)
    max_depth = options["max_depth"]
    min_depth = options["min_depth"]
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
    # cropped_matrix = crop_matrix(source.heightmap)
    # max_depth = np.max(cropped_matrix)
    # min_depth = np.min(cropped_matrix)
    # depth_range = max_depth - min_depth
    # # this always normalizes the heights to [0, 1], with the minimum value mapped to 0
    # # and the maximum value mapped to 1. This makes a relatively flat terrain extremely
    # # rugged, so this should change at some point.
    # normalized_matrix = (cropped_matrix - min_depth) / depth_range
    # raw_x, raw_y = geo_data.find_best_match(normalized_matrix)
    print('Begin', file=sys.stderr)
    raw_x, raw_y = location_seeker.get_coordinates(crop_matrix(source.heightmap))
    print('End', file=sys.stderr)
    return json.dumps(tuple(reversed(geo_data.pixels_to_coordinates((raw_x, raw_y)))))


@app.route('/config', methods=('GET', 'PUT'))
def config():
    if request.method == 'PUT':
        updates = request.get_json(force=True)
        updated_config = update_options(updates)
        return json.dumps(updated_config)
    else:
        return render_template('config.html.j2', options=options)


@app.route('/config/min-depth', methods=('PUT',))
def config_min_depth():
    min_depth = np.min(crop_matrix(source.heightmap))
    updated_options = update_options(dict(min_depth=min_depth))
    return json.dumps(updated_options)


@app.route('/config/max-depth', methods=('PUT',))
def config_max_depth():
    max_depth = np.max(crop_matrix(source.heightmap))
    updated_options = update_options(dict(max_depth=max_depth))
    return json.dumps(updated_options)

# source.run()
app.run("0.0.0.0", debug=False)
