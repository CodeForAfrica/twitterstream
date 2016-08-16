"""
Flask app
"""
import os
import requests
from flask import (Flask, g, request, session, redirect,
                   url_for, render_template, jsonify)
from flask_script import Manager
from twitterstream import config as config_file
from twitterstream.client import spawn_child

app = Flask(__name__,
            template_folder=os.getenv('TEMPLATES'),
            static_folder=os.getenv('STATIC'))
app.config.from_object(config_file)


def get_redis():
    if not hasattr(g, 'redis'):
        g.redis = redis.StrictRedis(**app.config['REDIS'])
    return g.redis



@app.route('/')
def home():
    '''
    index.html
    '''
    return render_template("index.html", source="home")


@app.route('/stream')
def stream():
    '''
    '''
    args = request.args.copy()
    remote_ip = request.environ["REMOTE_ADDR"]

    # verify captcha
    request_args = dict(response=args["g-recaptcha-response"],
            remoteip=remote_ip, secret=app.config["RECAPTCHA"]["secret_key"])
    resp = requests.post(app.config["RECAPTCHA"]["verify_url"], request_args)
    print "RECAPTCHA:  %s - %s" % (resp.status_code, resp.json())
    resp.raise_for_status()
    if resp.json()["success"]:
        filters = args["hashtag"]
        spawn_child("hashtag", args["hashtag"], app.config["SHEET_ID"])
        
        return render_template("index.html", source="stream")
    else:
        return render_template("index.html", source="fail")



manager = Manager(app)

if __name__ == "__main__":
    manager.run()
