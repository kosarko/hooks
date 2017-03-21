from flask import Flask
from flask import request
#from flask import jsonify

import json
from pprint import pformat

from hmac import HMAC
from hmac import compare_digest
import hashlib

import requests

import os
import logging

port = int(os.environ.get('PORT', 5000))
#logging.info('Listening on port {0}'.format(port))
debug = os.environ.get('DEBUG', 'False') == 'True'
secret = os.environ.get('SECRET').encode('utf8')
headers = {'Authorization': 'token ' + os.environ.get('GITHUB_API_KEY')}

if debug:
    logging.basicConfig(level=logging.DEBUG)
    logging.info('Set log level to {0}'.format(logging.getLevelName(logging.getLogger(__name__).getEffectiveLevel())))

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return "Hello, World!"


def add_label(issue_url, label):
    r = requests.post(issue_url + '/labels', json=[label], headers=headers)
    logging.debug(pformat(r))
    return "Got {}".format(r.status_code), r.status_code


def process_merged_pr(json_payload):
    action = json_payload.get('action', None)
    pull_request = json_payload.get('pull_request', None)
    logging.debug('pull_request=' + json.dumps(pull_request))
    if pull_request and action == 'closed' and pull_request['merged']:
        url = pull_request['issue_url']
        label = 'Merged in dev'
        return add_label(url, label)
    else:
        return "Doing nothing"


@app.route('/payload', methods=['POST'])
def payload():
    signature = 'sha1=' + HMAC(secret, msg=request.get_data(), digestmod=hashlib.sha1).hexdigest()
    if not compare_digest(signature, request.headers.get('X-Hub-Signature', default='')):
        logging.debug(signature)
        return "Signatures didn't match!", 500
    json_in = request.get_json()
    logging.debug(json_in)
    return process_merged_pr(json_in)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=debug, port=port)
