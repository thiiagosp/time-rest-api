import json
import flask
from ConfigParser import ConfigParser
from flask_httpauth import HTTPBasicAuth
import uuid
import shutil
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

config = ConfigParser()
auth = HTTPBasicAuth()

def getGts():
    proxyconffile = config.get('Proxy', 'conffile') 
    proxyconfig = ConfigParser()
    proxyconfig.read(proxyconffile)
    ip = proxyconfig.get('mars', 'ip')
    return [{
        'gt': gt[0],
        'ip': ip, 
        'port': gt[1]
    } for gt in proxyconfig.items('gts')]

def reloadConfigMiniGmlc():
    os.popen("{0} reload".format(config.get('Proxy', 'initscript')))

class InvallidParameter(Exception):
    def __init__(self, attlist):
        Exception.__init__(self, '')
        self.attlist = attlist
    def toError(self):
        return {'errors': [{
            'detail': '{0} is required'.format(att),
            'source': {'pointer': 'data/attributes/{0}'.format(att)}} for att in self.attlist] }

class DuplicatedParameter(Exception):
    def __init__(self, att):
        Exception.__init__(self, '')
        self.att = att
    def toError(self):
        return {'errors': [{
            'detail': '{0} already exists'.format(self.att),
            'source': {'pointer': 'data/attributes/{0}'.format(self.att)}}]}
        
class InvalidMinValue(Exception):
    def __init__(self, att, value):
        Exception.__init__(self, '')
        self.att = att
        self.value = value
    def toError(self):
        return {'errors': [{
            'detail': '{0} must be equal or greater than {1}'.format(self.att, self.value),
            'source': {'pointer': 'data/attributes/{0}'.format(self.att)}}] }

def loadDB(dbfile):
    with open(dbfile) as f:
        return json.loads(f.read())

def saveDB(db, dbfile):
    bkpfile = '{0}_{1}'.format(dbfile, datetime.now().strftime('%Y%m%d%H%M%S%f'))
    shutil.move(dbfile, bkpfile)
    with open(dbfile, 'w') as f:
        f.write(json.dumps(db, indent=4))
    return bkpfile

def findObj(db, objtype, objidid):
    return next((obj for obj in db[objtype] if str(obj['id']) == str(objidid)))

def checkAtts(d, atts):
    e = [att for att in atts if att not in d or not d[att]]
    if e: raise InvallidParameter(e)

def checkDuplicatedAttJson(obj, value, att):
    if value in obj: raise DuplicatedParameter(att)

def createObj(objlist, objtype, objdb, requiredAtts=[]):
    try:
        obj = json.loads(flask.request.data)[objtype]
        checkAtts(obj, requiredAtts)
        db = loadDB(objdb)
        obj['id'] = str(uuid.uuid1())
        obj['type'] = objtype
        db[objlist].append(obj)
        saveDB(db, objdb)
        return flask.make_response(flask.jsonify({objtype: obj}))
    except InvallidParameter as error:
        logger.error('createObj Exception: {0}'.format(error))
        return flask.make_response(flask.jsonify(error.toError())),422
    except Exception as error:
        logger.error('Exception Creating Object: {0} - {1} - {2}'.format(objlist, objtype, error))
        return flask.make_response(str(error)),500

def updateObj(id, objlist, objtype, objdb):
    try:
        cmd = json.loads(flask.request.data)[objtype]
        cmd['id'] = id
        cmd['type'] = objtype
        db = loadDB(objdb)
        oldcmd = findObj(db, objlist, id)
        db[objlist].remove(oldcmd)
        db[objlist].append(cmd)
        saveDB(db, objdb)
        return flask.make_response(flask.jsonify({}))
    except Exception as error:
        logger.error('Exception: {0}'.format(error))
        return flask.make_response(str(error)),500

def getObj(id, objlist, objtype, objdb):   
    try:
        obj = findObj(loadDB(objdb), objlist, id)
        return flask.make_response(flask.jsonify({objtype: obj}))
    except Exception as error:
        logger.error('Exception: {0}'.format(error))
        return flask.make_response(str(error)),500

def sortBy(arr, property, reverse=False):
	arr.sort(key=lambda x: x[property], reverse=reverse)
	return arr