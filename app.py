#!flask/bin/python
from functools import wraps
from flask import Flask, request, Response, config
from phue import Bridge
from pprint import pprint
import json
import yaml

app = Flask(__name__)
app.config.from_envvar('APP_CONFIG_FILE')

bridge = Bridge (app.config["BRIDGE_IP"])
bridge.connect()

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == app.config["USERNAME"] and password == app.config["PASSWORD"]

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/info/schedule')
@requires_auth
def get_schedule():
   return json.dumps(bridge.get_schedule())

@app.route('/scene/run', methods=['POST'])
@requires_auth
def run_scene():
   scene = request.json['scene']
   group = request.json['group']
   bridge.run_scene(group, scene)
   return "DONE"

if __name__ == '__main__':
   app.run(host='0.0.0.0', debug=False)
