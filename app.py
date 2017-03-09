from flask import Flask
from flask import request
from flask import jsonify

import os
#import logging

#logging.basicConfig(level=logging.INFO)

port = os.environ.get('PORT', 5000)
#logging.info('Listening on port {0}'.format(port))
debug = os.environ.get('DEBUG', False)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return "Hello, World!"

@app.route('/payload', methods=['POST'])
def payload():
    json_in = request.get_json()
    return jsonify(json_in)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=debug, port=port)
