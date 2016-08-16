"""
Flask app
"""
import os
from flask import (Flask, g, request, session, redirect,
                   url_for, render_template, jsonify)
from flask_script import Manager
from twitterstream import config as config_file

app = Flask(__name__,
            template_folder=os.getenv('TEMPLATES'),
            static_folder=os.getenv('STATIC'))
app.config.from_object(config_file)


def get_redis():
    if not hasattr(g, 'redis'):
        g.redis = redis.StrictRedis(**app.config['REDIS'])
    return g.redis



@app.route('/')
def counties():
    '''
    index.html
    '''
    args = request.args.copy()

        
    return render_template("index.html",
            )


manager = Manager(app)

if __name__ == "__main__":
    manager.run()
