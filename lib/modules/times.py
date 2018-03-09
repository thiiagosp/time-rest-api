from flask import Blueprint, request
import flask
import json
from ..common.common import config, auth, loadDB, checkAtts, InvallidParameter, saveDB, DuplicatedParameter, sortBy
import logging

logger = logging.getLogger(__name__)
module_times = Blueprint('module_times', __name__)


@module_times.route('/times', methods=['GET'])
# @auth.login_required
def getTimes():
    try:
        timesFile = config.get('Conf', 'timesfile')
        db = sortBy(loadDB(timesFile), 'id')
        return flask.make_response(flask.jsonify(db))
    except Exception as error:
        logger.error('Exception: {0}'.format(error))
        return flask.make_response(str(error)),500

@module_times.route('/time/<id>', methods=['GET'])
# @auth.login_required
def getTime(id):
    try:
        timesfile = config.get('Conf', 'timesfile')
        times = loadDB(timesfile)
        time = {}

        for t in times:
            if int(t["id"]) == int(id):
                time = t

        if not time:
            return flask.make_response(flask.jsonify({})), 404

        return flask.make_response(flask.jsonify(time)), 200
    except Exception as error:
        logger.error('Exception: {0}'.format(error))
        return flask.make_response(str(error)),500

@module_times.route('/user/times/<id>', methods=['GET'])
# @auth.login_required
def getUserTimes(id):
    try:
        timesfile = config.get('Conf', 'timesfile')
        times = loadDB(timesfile)
        userTimes = []

        for time in times:
            if int(time["user_id"]) == int(id):
                userTimes.append(time)

        if not userTimes:
            return flask.make_response(flask.jsonify({})), 404

        return flask.make_response(flask.jsonify(userTimes)), 200
    except Exception as error:
        logger.error('Exception: {0}'.format(error))
        return flask.make_response(str(error)),500

@module_times.route('/time', methods=['POST'])
# @auth.login_required
def postTime():
    try:
        time = json.loads(flask.request.data)
        checkAtts(time, ['user_id', 'date', 'type'])
       
        timesfile = config.get('Conf', 'timesfile')
        times = loadDB(timesfile)

        aid = len(times)
        t = {}
        t['id'] = aid
        t['user_id'] = time['user_id']
        t['date'] = time['date']
        t['type'] = time['type']        

        times.append(t)
        saveDB(times, timesfile)
        return flask.make_response(flask.jsonify({'time': time})), 201
    except InvallidParameter as error:
        logger.error('Exception: {0}'.format(error))
        return flask.make_response(flask.jsonify(error.toError())), 422
    except DuplicatedParameter as error:
        logger.error('Exception: {0}'.format(error))
        return flask.make_response(flask.jsonify(error.toError())), 422
    except Exception as error:
        logger.error('Exception: {0}'.format(error))
        return flask.make_response(str(error)), 500

@module_times.route('/time/<id>', methods=['PUT'])
# @auth.login_required
def putTime(id):
    try:
        updatedddTime = json.loads(flask.request.data)
        checkAtts(updatedddTime, ['id', 'user_id', 'date', 'type'])
        timesfile = config.get('Conf', 'timesfile')
        times = loadDB(timesfile)
        time = {}

        for t in times:
            if int(t["id"]) == int(id):
                time = t

        if not time:
            return flask.make_response(flask.jsonify({})), 404
        
        time['user_id'] = updatedddTime['user_id']
        time['date'] = updatedddTime['date']
        time['type'] = updatedddTime['type']

        saveDB(times, timesfile)
        return flask.make_response(flask.jsonify({})), 200
    except Exception as error:
        logger.error('Exception: {0}'.format(error))
        return flask.make_response(str(error)), 500

@module_times.route('/time/<id>', methods=['DELETE'])
# @auth.login_required
def deleteTime(id):
    try:
        timesfile = config.get('Conf', 'timesfile')
        times = loadDB(timesfile)
    
        times = [x for x in times if int(x['id']) != int(id)]

        saveDB(times, timesfile)
        return flask.make_response(flask.jsonify({})), 204
    except Exception as error:
        logger.error('Exception: {0}'.format(error))
        return flask.make_response(str(error)), 500