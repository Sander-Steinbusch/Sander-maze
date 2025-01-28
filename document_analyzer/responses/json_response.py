from flask import Response
from json import dumps

def  build_json_response(dictionary):
    response = Response(dumps(dictionary))
    response.headers["Content-Type"] = "application/json"
    return response
