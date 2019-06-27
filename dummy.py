import glob
import random

from flask import Flask, send_file

app = Flask(__name__)


@app.route('/height.raw')
def height():
    files = glob.glob('data/dummy/*.raw')
    return send_file(random.choice(files))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
