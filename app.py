from flask import Flask
from flask import request

import json
from pprint import pformat

from hmac import HMAC
from hmac import compare_digest
import hashlib

import requests

import os
import logging
import re

port = int(os.environ.get('PORT', 5000))
# logging.info('Listening on port {0}'.format(port))
debug = os.environ.get('DEBUG', 'False') == 'True'
secret = os.environ.get('SECRET').encode('utf8')
headers = {'Authorization': 'token ' + os.environ.get('GITHUB_API_KEY')}
dev_branch_name = os.environ.get('DEV_BRANCH_NAME')

if debug:
    logging.basicConfig(level=logging.DEBUG)
    logging.info('Set log level to {0}'.format(logging.getLevelName(logging.getLogger(__name__).getEffectiveLevel())))

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return "Hello, World!"


def add_label(*args, **kwargs):
    response = ""
    status = 200
    for issue_url in args:
        if issue_url:
            r = requests.post(issue_url + '/labels', json=[kwargs['label']], headers=headers)
            logging.debug(pformat(r))
            response += "{}: Got {}".format(issue_url, r.status_code)
            status = r.status_code if r.status_code > status else status
    return response, status


def remove_label(issue_url, label):
    response = ""
    status = 200
    if issue_url:
        r = requests.delete(issue_url + '/labels/' + label,  headers=headers)
        logging.debug(pformat(r))
        response += "{}: Got {}".format(issue_url, r.status_code)
        status = r.status_code if r.status_code > status else status
    if status >= 300:
        logging.error(pformat(r))
    return response, status


def process_merged_pr(json_payload):
    action = json_payload.get('action', None)
    pull_request = json_payload.get('pull_request', None)
    logging.debug('pull_request=' + json.dumps(pull_request))
    if pull_request and action == 'closed' and\
            pull_request['merged'] and pull_request['base']['label'] == dev_branch_name:
        pull_request_url = pull_request['issue_url']
        # assume the pr branch name has an issue number assigned...like issue_#123
        assigned_issue_url = None
        m = re.search('\D*#(\d+)\D*', pull_request['head']['ref'])
        if m:
            issues_url = json_payload.get('repository')['issues_url']
            assigned_issue_url = issues_url.format(**{'/number': '/' + m.group(1)})
        label = 'Merged in dev'
        remove_label(assigned_issue_url, 'Has PR')
        return add_label(pull_request_url, assigned_issue_url, label=label)
    else:
        return "Doing nothing"


@app.route('/payload', methods=['POST'])
def payload():
    if 'pull_request' != request.headers.get('X-GitHub-Event', default=''):
        logging.debug(request.headers.get('X-GitHub-Event'))
        return "Wrong event type!", 500

    signature = 'sha1=' + HMAC(secret, msg=request.get_data(), digestmod=hashlib.sha1).hexdigest()
    if not compare_digest(signature, request.headers.get('X-Hub-Signature', default='')):
        logging.debug(signature)
        return "Signatures didn't match!", 500

    json_in = request.get_json()
    logging.debug(json_in)
    return process_merged_pr(json_in)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=debug, port=port)
