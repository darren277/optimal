""""""
import json

def test_unconstrained_optimization_basic(client):
    response = client.handle_request(
        method='GET',
        path='/unconstrained_optimization',
        query_string='a=100&b=2',
        headers={},
        body=''
    )
    assert response['statusCode'] == 200
    data = json.loads(response['body'])
    assert 'p_star' in data
    assert 'R_star' in data
    assert isinstance(data['p_star'], int)
    assert isinstance(data['R_star'], int)


def test_loading_scipy(client):
    response = client.handle_request(method='GET', path='/test_loading_scipy', headers={}, body='')
    assert response['statusCode'] == 200
    assert 'scipy_version' in json.loads(response['body'])
    assert 'success' in json.loads(response['body'])


def test_loading_pulp(client):
    response = client.handle_request(method='GET', path='/test_loading_pulp', headers={}, body='')
    assert response['statusCode'] == 200
    assert 'pulp_version' in json.loads(response['body'])
    assert 'success' in json.loads(response['body'])


def test_loading_sympy(client):
    response = client.handle_request(method='GET', path='/test_loading_sympy', headers={}, body='')
    assert response['statusCode'] == 200
    assert 'sympy_version' in json.loads(response['body'])
    assert 'success' in json.loads(response['body'])


def test_index_returns_html(client):
    response = client.handle_request(method='GET', path='/', headers={}, body='')
    assert response['statusCode'] == 200
    assert 'text/html' in response.headers['Content-Type']
    assert '<!DOCTYPE html>' in response['body'].decode('utf-8')


def test_llm_endpoint_mocked(client, monkeypatch):
    # Patch boto3 to prevent real Lambda call
    import json
    class FakeClient:
        def invoke(self, **kwargs):
            class FakePayload:
                def read(self):
                    return json.dumps({
                        "structured_response": {
                            "description": "Test problem",
                            "classification": "Linear programming"
                        }
                    }).encode('utf-8')
            return {"Payload": FakePayload()}

    import boto3
    monkeypatch.setattr(boto3, 'client', lambda service: FakeClient())

    response = client.handle_request(
        method='GET',
        path='/llm_endpoint',
        query_string='problem_description=Maximize+profit+subject+to+constraints',
        headers={},
        body=''
    )
    assert response['statusCode'] == 200
    data = json.loads(response['body'])
    assert 'structured_response' in data
    assert data['structured_response']['classification'] == 'Linear programming'
