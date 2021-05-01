# this function needs to fix from the main part................. ( even code incorrect from javascript)
def typeArray(val):
    r = []
    for v in val:
        v_type = type(v)
        if not (type in r):
            r.append(v_type)
    return {'type': r}


def typeValue(val):
    if isinstance(val, list):
        return {'type': 'array', 'items': typeArray(val)}
    # check if it is an object or not!!!!!
    if isinstance(val, dict):
        properties = getProperties(val)
        return {'type': 'object', 'properties': properties, 'required': properties.keys()}

    if isinstance(val, int):
        return {'type': 'integer'}
    
    return {'type': type(val)}

def getProperties(j):
    print("!!!!!!!!!!!!!!!!!!! this instance is not checked yet")
    k = j.keys()
    for name in k:
        j[name] = typeValue(j[name])
    return j


def getSchema(json_object):
    schema = {}

    # print("!!!!!!!!!!!!!!!!!!!! getSchema in json_schema_infer is not completed.....")

    schema['$schema'] = 'http://json-schema.org/schema#'
    schema['title'] = 'JSON inferred schema'
    schema['description'] = 'JSON inferred schema'
    schema['type'] = 'object'
    try:
        schema['properties'] = getProperties(json_object)
        schema['required'] = schema['properties'].keys()
    except:
        schema['properties'] = {}
        schema['required'] = schema['properties'].keys()

    return schema