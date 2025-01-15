""""""
import time
import requests

BASE_URL='http://optimal.apphosting.services'


def test_loading_dependency(dep: str):
    ts = time.time()
    req = requests.get(f'{BASE_URL}/test_loading_{dep}')
    assert req.status_code == 200
    data = req.json()

    assert f'{dep}_version' in data
    assert f'SUCCESSFULLY LOADED {dep.upper()}' in data['success']
    assert 'loading_time' in data

    print(data)
    print(f"Test took {time.time() - ts} seconds")

test_loading_dependency('pyomo')
test_loading_dependency('pulp')
test_loading_dependency('sympy')
