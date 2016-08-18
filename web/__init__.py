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
    return render_template("index.html",
            source="home", remote_ip=request.environ["REMOTE_ADDR"])


@app.route('/stream')
def stream():
    '''
    '''
    args = request.args.copy()
    remote_ip = request.environ["REMOTE_ADDR"]

    # verify captcha
    request_args = dict(response=args["g-recaptcha-response"],
            remoteip=remote_ip, secret=app.config["RECAPTCHA"]["secret_key"])
    resp = requests.post(
            app.config["RECAPTCHA"]["verify_url"], request_args,
            timeout=app.config["TIMEOUTS"]["recaptcha"])
    resp.raise_for_status()
    if resp.json()["success"]:
        invalid = False
        hashtags = validate_hashtags(str(args["hashtag"]))
        sheet_id = validate_sheet_id(str(args["sheetid"]))
        if hashtags and sheet_id:
            spawn_child("hashtag", hashtags, sheet_id)
        elif hashtags:
            invalid = "sheet_id"
        elif sheet_id:
            invalid = "hashtags"
        else:
            invalid = "hashtags and sheet_id"
    else:
        invalid = "captcha"
    
    return render_template("index.html", source="stream", invalid=invalid)


def validate_hashtags(hashtags=""):
    '''
    return validated parameter or False
    '''
    if len(hashtags) >= 140 or len(hashtags) <= 1:
        return False
    return hashtags
    


def validate_sheet_id(sheet_id=""):
    '''
    return validated parameter or False
    '''
    try:
        # 1. call Google Sheets to confirm existence of the spreadsheet
        sheets_url = "https://docs.google.com/spreadsheets/d/" + str(sheet_id).strip()
        resp = requests.get(sheets_url, timeout=app.config["TIMEOUTS"]["googlesheets"])
        resp.raise_for_status()
        status_code = resp.status_code
        url_after = resp.url
        if status_code == 200 and (
                url_after.startswith("https://accounts.google.com/") or\
                        url_after.startswith("https://docs.google.com/spreadsheets")):
            # valid document
            return str(sheet_id).strip()
        else:
            print "Sheet ID %s :: %s" % (sheet_id, resp.status_code)
            return False


    except Exception, err:
        print "ERROR validate_sheet_id failed for sheedID %s -- %s" % (sheet_id, err)
        return False


manager = Manager(app)

if __name__ == "__main__":
    manager.run()
