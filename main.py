#!/usr/bin/python

import flask
from flask_compress import Compress
from flask_cors import CORS
from lib.common import authentication
from lib.common.common import config, auth
from lib.modules.times import module_times

import logging
import logging.config
import sys
import signal
import asyncore
import datetime, time

logger = logging.getLogger()

compress = Compress()
app = flask.Flask(__name__)
app.register_blueprint(module_times)

CORS(app)

@auth.error_handler
def custom_401():
    return flask.jsonify({'error': 'Invalid Credentials'})

@auth.verify_password
def verifyPassword(username, password):
    auth = flask.request.headers.get('Authorization')
    if auth:
        return authentication.verifyAuthToken(auth)
    else:
        username = flask.request.form.get('username')
        password = flask.request.form.get('password')
        return authentication.verifyPassword(username, password)

@app.route('/token', methods=['POST'])
@auth.login_required
def getAuthToken():
    username = flask.request.form.get('username')
    user_id = authentication.getId(flask.request.form.get('username'))
    expiration = config.getint('Conf', 'expiration_token')
    access_token = authentication.generateAuthToken(user_id, expiration)

    token = {
        'access_token': access_token.decode('ascii'), 
        'expiration': int(expiration) * 1000, 
        'currentUser': username
    }

    return flask.make_response(flask.jsonify(token))

def signalHandler(signum, _):
    print('System Signal [signal: %s(%d)]' % (next((k for k, v in signal.__dict__.iteritems() if v == signum), 'ERROR'), signum))
    asyncore.close_all()
    #raise asyncore.ExitNow('System signaled to stop')
    sys.exit(0)

def main():
    if len(sys.argv) != 2:
        print('Usage: {0} [config_filename]'.format(sys.argv[0]))
        sys.exit(1)

    configfilename = sys.argv[1]
    logging.config.fileConfig(configfilename, disable_existing_loggers=False)
    config.read(configfilename)

    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)
    #signal.signal(signal.SIGHUP, signalHandler)

    lport = config.getint('Conf', 'port')
    compress.init_app(app)
    app.run(host= '0.0.0.0', port=lport, debug=True, threaded=True)

if __name__ == '__main__':
    main()
