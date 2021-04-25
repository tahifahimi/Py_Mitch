# sensitivity.py
import numpy as np

"""why does it use all 52 features not 45 ones of them????????????????"""
def countParams(req):
    return len(req['params'])

def countBools(req):
    numberBools = 0
    for p in req['params'].keys():
        print(req['params'][p])
        if req['params'][p] == 'True' or req['params'][p] == 'False' or req['params'][p] == '1' or req['params'][p] == '0':
            numberBools += 1
    print("number of bools are : ", numberBools)
    return numberBools


import re
def countIds(req):
    numOfIds = 0
    prog = re.compile('^[0-9]{14}|[0-9\-a-fA-F]{20,}$')
    for p in req['params'].keys():
        if req['params'][p] is not None:
            if prog.match(req['params'][p][0]) is not None:
                numOfIds += 1
    return numOfIds


def countBlobs(req):
    numOfBlobs = 0
    prog = re.compile('^[^\s]{20,}$')
    for p in req['params'].keys():
        if req['params'][p]:
            if prog.match(req['params'][p][0]) != None:
                numOfBlobs += 1
    return numOfBlobs

# length of the params keys and values
def getReqLen(req):
    l = 0
    for p in req['params'].keys():
        if req['params'][p]:
            l = l + len(p) + len(req['params'][p])
    return l

# changed the concept of this method .... used new implementation
def isInPath(req, k):
    if k.lower() in req['url'].lower():
        return 1
    else:
        return 0

# changed the concept of this method .... used new implementation
def isInParam(req, k):
    for p in req['params'].keys():
        if k.lower() in p.lower():
            return 1
    return 0


def isSensitive(req, classifier):
    fetureVector = []

    if req['method'].upper() == "PUT" or req['method'].upper == "DELETE":
        return True
    if req['method'].upper() == "OPTIONS":
        return False
    # numberOfParams
    fetureVector.append(countParams(req))
    # numberOfBools
    fetureVector.append(countBools(req))
    # numberOfIds
    fetureVector.append(countIds(req))
    # numberOfBlobs
    fetureVector.append(countBlobs(req))
    # reqLen
    fetureVector.append(getReqLen(req))

    keywords = ['create', 'add', 'set', 'delete', 'update', 'remove',
                'friend', 'setting', 'password', 'token', 'change', 'action',
                'pay', 'login', 'logout', 'post', 'comment', 'follow', 'subscribe', 'sign', 'view']
    # ????????????????????????????.........................................
    for k in keywords:
        fetureVector.append(isInPath(req, k))
        fetureVector.append(isInParam(req, k))

    methods = ['PUT', 'DELETE', 'POST', 'GET', 'OPTIONS']
    for m in methods:
        if m == req['method'].upper():
            fetureVector.append(1)
        else:
            fetureVector.append(0)

    # now run javascript model here
    sensitivity = classifier.predict([np.array(fetureVector)])
    return sensitivity[0]