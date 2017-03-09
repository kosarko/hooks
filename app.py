from flask import Flask
from flask import request
from flask import jsonify

import os

port = os.environ.get('PORT', 5000)
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
    app.run(debug=debug, port=port)
