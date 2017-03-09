from flask import Flask
from flask import request
from flask import jsonify

import os
import logging

port = int(os.environ.get('PORT', 5000))
#logging.info('Listening on port {0}'.format(port))
debug = os.environ.get('DEBUG', 'False') == 'True'

if debug:
    logging.basicConfig(level=logging.DEBUG)
    logging.info('Set log level to {0}'.format(logging.getLevelName(logging.getLogger(__name__).getEffectiveLevel())))

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return "Hello, World!"

@app.route('/payload', methods=['POST'])
def payload():
    json_in = request.get_json()
    logging.debug(json_in)
    return jsonify(json_in)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=debug, port=port)
