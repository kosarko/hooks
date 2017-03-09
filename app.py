#!/home/okosarko/.conda/envs/my_root/bin/python
from flask import Flask
from flask import request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def index():
    print(request.get_json(force=True))
    return "Hellow, World!"

if __name__ == '__main__':
    app.run(debug=True)
