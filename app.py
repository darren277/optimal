""""""
import io
import json
from os import path
import os

import time
from datetime import datetime

import boto3 as boto3
from chalice import Chalice, Response
from jinja2 import Environment, FileSystemLoader, BaseLoader


app = Chalice(app_name="optimal")

cwd = path.dirname(__file__)
env = Environment(loader=FileSystemLoader(path.join(cwd, 'chalicelib', 'frontend'), encoding='utf8'))
s3_env = Environment(loader=BaseLoader())

USER_DATA_TABLE = 'userdata'


# https://temporarytestbucket123412341234.s3.amazonaws.com/frontend/index.html

OUTPUT_QUEUE_NAME = os.environ['QUEUE_NAME']

s3 = boto3.resource('s3')
sqs = boto3.client("sqs")
dynamodb = boto3.resource("dynamodb")
# posts = dynamodb.Table('optimal-posts')


app.debug = True


@app.route('/test_loading_pyomo')
def test_loading_pyomo():
    import time
    start_time = time.time()
    import pyomo
    print("SUCCESSFULLY LOADED PYOMO", pyomo.__version__)
    return {'pyomo_version': pyomo.__version__, 'success': 'SUCCESSFULLY LOADED PYOMO', 'loading_time': time.time() - start_time}

@app.route('/test_loading_scipy')
def test_loading_scipy():
    #import scipy
    #print("SUCCESSFULLY LOADED SCIPY", scipy.__version__)
    print("NOT YET IMPLEMENTED")
    return {'success': 'NOT YET IMPLEMENTED'}

@app.route('/test_loading_pulp')
def test_loading_pulp():
    import time
    start_time = time.time()
    import pulp
    print("SUCCESSFULLY LOADED PULP", pulp.__version__)
    return {'pulp_version': pulp.__version__, 'success': 'SUCCESSFULLY LOADED PULP', 'loading_time': time.time() - start_time}

@app.route('/test_loading_sympy')
def test_loading_sympy():
    import time
    start_time = time.time()
    import sympy
    print("SUCCESSFULLY LOADED SYMPY", sympy.__version__)
    return {'sympy_version': sympy.__version__, 'success': 'SUCCESSFULLY LOADED SYMPY', 'loading_time': time.time() - start_time}


def ts():
    t = datetime.fromtimestamp(time.time())
    str_date_time = t.strftime("%Y%m%d%H%M%S%f")
    return str_date_time
