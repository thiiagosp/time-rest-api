import json
import uuid
import hashlib
import sys
from common import config
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

#authfilename = 'data/authentication.json'
seckey = str(uuid.uuid1())

def loadCfg():
    authfilename = config.get('Conf', 'authenticationfile')
    with open(authfilename) as f:
        return json.load(f)

def saveCfg(userdb):
    authfilename = config.get('Conf', 'authenticationfile')
    with open(authfilename, 'w') as f:
        json.dump(userdb, f, indent=4)

def hashIt(data):
    return hashlib.sha512(data).hexdigest()

def isValidId(userid):
    userdb = loadCfg()
    return next((True for user in userdb if userid == user.get('id', '')), False)

def getId(username):
    userdb = loadCfg()
    return next((user.get('id',None) for user in userdb if username == user.get('username', '')), None)

def verifyPassword(username, password):
    userdb = loadCfg()
    return next((True for user in userdb if username == user.get('username', '') and password == user.get('password', '')), False)

def generateAuthToken(user_id, expiration):
    s = Serializer(seckey, expires_in = expiration)
    return s.dumps({ 'id': user_id })

def verifyAuthToken(token):
    try:
        token = token.lstrip('Bearer').strip()
        s = Serializer(seckey)
        data = s.loads(token)
        userid = data.get('id', None)
        return userid and isValidId(userid)
    except SignatureExpired:
        return None # valid token, but expired
    except BadSignature:
        return None # invalid token

if __name__ == '__main__':
    userdb = loadCfg()
    user = {}
    user['id'] = str(uuid.uuid1())
    user['username'] = sys.argv[1]
    user['password'] = hashIt(sys.argv[2])
    userdb.append(user)
    saveCfg(userdb)
