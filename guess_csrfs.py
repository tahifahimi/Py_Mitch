import json
import datetime

from json_schema_infer import *


def isSameReq(base, test):
    if base['url'] != test['url']:
        return False
    for k in base['params'].keys():
        if not (k in test['params']):
            return False

    for p in test['params'].keys():
        if not (p in base['params']):
            return False
    return True


# remove the type in here ......................???????????????//// check this later---> object is a dict in python
def isDic(v):
    return isinstance(v, dict) and (not (v is None)) and (not isinstance(v, list)) and (not isinstance(v, datetime.date))
    # return type(v) == 'object' and (not (v is None)) and (not isinstance(v, list)) and (not isinstance(v, datetime.date))
    # return (not (v is None)) and (not isinstance(v, list)) and (not isinstance(v, datetime.date))


def isSameSchema(sA, sB):
    for k in sA.keys():
        if not (k in sB):
            return False
        else:
            if isDic(sA[k]) and isDic(sB[k]) and (not isSameSchema(sA[k], sB[k])):
                return False
            elif sA[k] != sB[k]:
                return False

    return True


def hasSameJSONSchema(a, b):
    sA = getSchema(a)
    sB = getSchema(b)

    ret = isSameSchema(sA, sB)
    return ret


def isHTML(s):
    if "</html>" in s['body'].lower():
        return True
    if 'Content-Type' in s['headers'] and "text/html" in s['headers']['Content-Type']:
        return True
    return False


def isJson(s):
    try:
        j = json.dump(s['body'])
        if isinstance(j, int):
            return False
    except:
        return False

    return True


def compare_requests(rA, rB):
    result = {
        'url': rA['url'],
        'params': rA['params'],
        'overall': 'same',
        'method': {},
        'status': {},
        'body': {'ans': 'same'}
    }
    statusA = rA['response']['status']
    statusB = rB['response']['status']

    if statusA == statusB:
        result['status']['ans'] = 'same'
    else:
        result['status']['ans'] = 'different'
        result['overall'] = 'different'

    result['status']['valueA'] = statusA
    result['status']['valueB'] = statusB

    # checking the body type
    if isHTML(rA['response']):
        result['body']['typeA'] = 'html'
    elif isJson(rA['response']):
        result['body']['typeA'] = 'json'
    else:
        result['body']['typeA'] = 'plaintext'

    if isHTML(rB['response']):
        result['body']['typeB'] = 'html'
    elif isJson(rB['response']):
        result['body']['typeB'] = 'json'
    else:
        result['body']['typeB'] = 'plaintext'

    min_length = min(len(rA['response']['body']), len(rB['response']['body']))
    max_length = max(len(rA['response']['body']), len(rB['response']['body']))

    result['body']['ratio'] = (min_length + 1) / (1.0 * max_length + 1)

    if result['body']['typeA'] == 'JSON' and result['body']['typeB'] == 'JSON':
        json_a = json.dump(rA['response']['body'])
        json_b = json.dump(rB['response']['body'])
        if hasSameJSONSchema(json_a, json_b):
            result['body']['ans'] = 'same'
        else:
            result['body']['ans'] = 'different'
            result['overall'] = 'different'
    elif result['body']['typeA'] == 'html' and result['body']['typeB'] == 'html':
        if result['body']['ratio'] < 0.99:
            result['body']['ans'] = 'different'
            result['overall'] = 'different'

    elif result['body']['typeA'] == 'plaintext' and result['body']['typeB'] == 'plaintext':
        if rA['response']['body'] != rB['response']['body']:
            result['body']['ans'] = 'different'
            result['overall'] = 'different'

    else:
        if result['body']['typeA'] != result['body']['typeB']:
            result['body']['ans'] = 'different'
            result['overall'] = 'different'

    result['body']['valueA'] = rA['response']['body']
    result['body']['valueB'] = rB['response']['body']

    print("result in guess CSRF is : ", result)
    return result


def compare_sensitive_requests(runA, runB):
    results = []
    for rA in runA:
        found = False
        for rB in runB:
            if isSameReq(rA, rB):
                found = True
                # compare two equal request
                results.append(compare_requests(rA, rB))
        if not found:
            print("couldn't find request: ", rA['url'])
    
    return results

def isSameEndPoint(base, test):
    if base['url'] != test['url']:
        return False

    for k in base['params'].keys():
        if not (k in test['params']):
            return False

    for p in test['params'].keys():
        if not (p in base['params']):
            return False

    return True


def findRequest(needle, haystack):
    for r in haystack:
        if isSameEndPoint(needle, r):
            return r

    print("!!!!no matching endpoint found for ", needle['url'])
    return False

def guessCSRFs(alice, alice1, bob, unauth):
    print("comparing traces...")
    alice_vs_unauth = compare_sensitive_requests(alice, unauth)
    alice_vs_alice1 = compare_sensitive_requests(alice, alice1)
    alice_vs_bob = compare_sensitive_requests(alice, bob)
    candidates = []
    print("comparison analysis ...")
    print("confirming sensitivity ... ")

    for r in alice_vs_unauth:
        print("checking ... ", r['url'])
        if r['overall'] == 'different':
            print("candidate added")
            candidates.append(r)

    resulting_candidates = []
    print("confirming reachability ... ")
    for c in candidates:
        print("checking :", c['url'])
        r_avb = findRequest(c, alice_vs_bob)
        r_ava1 = findRequest(c, alice_vs_alice1)

        if r_avb['overall'] == ' different' and r_ava1['overall'] == 'different':
            continue
        resulting_candidates.append(c)
    
    return candidates, resulting_candidates
