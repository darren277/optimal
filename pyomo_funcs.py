""""""

def test_loading_pyomo_func(event, context):
    import time
    start_time = time.time()
    import pyomo
    print("SUCCESSFULLY LOADED PYOMO (DOCKER CONTAINER)", pyomo.__version__)
    return {'pyomo_version': pyomo.__version__, 'success': 'SUCCESSFULLY LOADED PYOMO (DOCKER CONTAINER)', 'loading_time': time.time() - start_time}
