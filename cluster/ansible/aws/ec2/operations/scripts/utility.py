import json
#print(json.__file__)

from datetime import date, datetime

class DateTimeEncoder(json.JSONEncoder):
    #return(json.dumps(arg, indent=4, cls=DateTimeEncoder))

    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        serial = obj.isoformat()
        return serial
    raise TypeError ("Type %s not serializable" % type(obj))

def json_dump(arg):
    #return(json.dumps(arg, indent=4, default=json_serial))
    return(json.dumps(arg, indent=4, cls=DateTimeEncoder, sort_keys=True))
