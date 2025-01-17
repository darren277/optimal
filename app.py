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

@app.lambda_function(name='test_loading_scipy_func')
def test_loading_scipy_func(event, context):
    import time
    start_time = time.time()
    import scipy
    print("SUCCESSFULLY LOADED SCIPY", scipy.__version__)
    return {'scipy_version': scipy.__version__, 'success': 'SUCCESSFULLY LOADED SCIPY', 'loading_time': time.time() - start_time}

@app.route('/test_loading_scipy')
def test_loading_scipy():
    lambda_client = boto3.client('lambda')
    try:
        response = lambda_client.invoke(
            FunctionName='optimal-dev-test_loading_scipy_func',
            InvocationType='RequestResponse',
            Payload=b'{}'
        )
        data = json.loads(response['Payload'].read())
        return data
    except Exception as e:
        return {'error': str(e)}, 500


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

@app.route('/test_loading_dwave')
def test_loading_dwave():
    lambda_client = boto3.client('lambda')
    try:
        response = lambda_client.invoke(
            FunctionName='optimal-dev-test_loading_dwave_func',
            InvocationType='RequestResponse',
            Payload=b'{}'
        )
        data = json.loads(response['Payload'].read())
        return data
    except Exception as e:
        return {'error': str(e)}, 500

#djikstra(destinations_graph, 'Vancouver,Canada', 'Vancouver,Canada')


def ts():
    t = datetime.fromtimestamp(time.time())
    str_date_time = t.strftime("%Y%m%d%H%M%S%f")
    return str_date_time


def unconstrained_optimization(a: int, b: int):
    import sympy as sp

    # Define parameters (A, B) as positive for economic interpretation
    A, B = sp.symbols('A B', positive=True, real=True)

    # Define the price variable p (can restrict to p >= 0, but let's keep it real for simplicity)
    p = sp.Symbol('p', real=True)

    # Revenue function: R(p) = p * (A - B*p)
    R = p * (A - B * p)


    first_derivative = sp.diff(R, p)
    critical_points = sp.solve(first_derivative, p)
    print("Critical points:", critical_points)

    second_derivative = sp.diff(first_derivative, p)

    for c_p in critical_points:
        print(f"Second derivative at p={p}: {second_derivative.subs(p, c_p)}")

    p_star = critical_points[0].subs({A: a, B: b})
    R_star = R.subs({p: p_star, A: a, B: b})

    print(f"\nNumerical Example (A={a}, B={b}):")
    print(f"Optimal price p* = {p_star}")
    print(f"Maximum revenue R* = {R_star}")

    return dict(
        p_star=int(p_star),
        R_star=int(R_star),
        #critical_points=critical_points
    )

# a = 100, b = 1

@app.route('/unconstrained_optimization')
def unconstrained_optimization_route():
    a = app.current_request.query_params.get('a', 100)
    b = app.current_request.query_params.get('b', 1)
    return unconstrained_optimization(int(a), int(b))

