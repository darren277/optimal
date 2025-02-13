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
    lambda_client = boto3.client('lambda')
    try:
        response = lambda_client.invoke(
            FunctionName='optimal-dev-test_loading_pyomo_func',
            InvocationType='RequestResponse',
            Payload=b'{}'
        )
        data = json.loads(response['Payload'].read())
        return data
    except Exception as e:
        return {'error': str(e)}, 500

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


class LLM_ENV:
    SYSTEM_PROMPT_FOR_CLASSIFIER = """
You are a helpful expert assistant for people who need to solve optimization problems.

Your task is to take in plain English descriptions of optimization problems and classify them into one of the following:
1. Unconstrained optimization.
2. Equality-constrained optimization.
3. Linear programming.
4. Quadratic programming.
5. Nonlinear programming.
6. Integer programming.
7. Mixed-integer programming.
8. Other or not an optimization problem.

You can ask clarifying questions to help you make a decision. You can also ask for more information if you need it.
    """

    SYSTEM_PROMPT_FOR_SYMBOLIC_TRANSLATION = """
You are a helpful expert assistant for people who need to solve optimization problems.

The optimization problem category is: {problem_classification}.

Your task is to take in plain English descriptions of optimization problems and translate them into symbolic form.

If you cannot structure the problem in symbolic form, you will have to state that you cannot do it and provide a reason why.
    """

    def get_structured_outputs(self):
        from pydantic import BaseModel
        from enum import Enum

        class ProblemClassification(str, Enum):
            UNCONSTRAINED = "Unconstrained optimization"
            EQUALITY_CONSTRAINED = "Equality-constrained optimization"
            LINEAR = "Linear programming"
            QUADRATIC = "Quadratic programming"
            NONLINEAR = "Nonlinear programming"
            INTEGER = "Integer programming"
            MIXED_INTEGER = "Mixed-integer programming"
            OTHER = "Other or not an optimization problem"

        class OptimizationProblem(BaseModel):
            description: str
            classification: ProblemClassification

        return OptimizationProblem


def load_key_from_secret_manager(secret_name):
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name='us-east-1')

    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    secret = get_secret_value_response['SecretString']
    return json.loads(secret)


@app.lambda_function(name='llm_endpoint_func')
def llm_endpoint_func(event, context):
    import time
    structured_response = dict()
    start_time = time.time()
    import openai
    print('EVENT:', event)
    print("SUCCESSFULLY LOADED OPENAI", openai.__version__)

    api_key = load_key_from_secret_manager('OPTIMAL_OPENAI_API_KEY')['OPTIMAL_OPENAI_API_KEY']
    try:
        openai_client = openai.Client(api_key=api_key)
    except:
        return {'error': 'FAILED TO LOAD OPENAI'}

    user_message = event.get('problem_description')

    if not user_message:
        return {'error': 'NO PROBLEM DESCRIPTION PROVIDED'}

    OptimizationProblem = LLM_ENV().get_structured_outputs()
    # Supported models: o1-2024-12-17 and later, gpt-4o-mini-2024-07-18 and later, gpt-4o-2024-08-06 and later

    # simple chat completion test...
    model = "gpt-4o-2024-08-06"
    messages = [
        {"role": "system", "content": "You are a helpful expert assistant for people who need to solve optimization problems."},
        {"role": "user", "content": user_message},
        ##{"role": "user", "content": "I have a problem with a linear programming model."},
        ##{"role": "system", "content": "I can help you with that. Please provide more details about your problem."},
        ##{"role": "user", "content": "I have 3 variables and 2 constraints."},
        ##{"role": "system", "content": "Great! I will help you with that. Please provide the coefficients of the objective function and the constraints."}
    ]
    try:
        result = openai_client.beta.chat.completions.parse(
            model=model,
            messages=messages,
            response_format=OptimizationProblem
        )
        print('RESULT:', result)
        try:
            choices = result.choices
            top_choice = choices[0]
            assistant_message = top_choice.message.content

            structured = json.loads(assistant_message)
            description = structured['description']
            classification = structured['classification']

            structured_response.update(
                description=description,
                classification=classification
            )
        except Exception as e:
            assistant_message = str(e)
    except Exception as e:
        print(e)
        return {'error': 'FAILED TO COMPLETE CHAT', 'msg': str(e)}
    return {'openai_version': openai.__version__, 'success': 'SUCCESSFULLY LOADED OPENAI', 'loading_time': time.time() - start_time,
            'result': assistant_message, 'structured_response': structured_response}

@app.route('/llm_endpoint')
def llm_endpoint():
    args = app.current_request.query_params
    serialized_args = {key: val for key, val in args.items()} if args else {}

    lambda_client = boto3.client('lambda')
    try:
        response = lambda_client.invoke(
            FunctionName='optimal-dev-llm_endpoint_func',
            InvocationType='RequestResponse',
            Payload=json.dumps(serialized_args)
        )
        data = json.loads(response['Payload'].read())
        print('data', data)
        err = data.get('error')
        if err:
            return {'error': err}, 500
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

