""""""

def test_loading_dwave_func(event, context):
    import time
    start_time = time.time()
    import networkx
    import dimod
    import networkx as nx
    import dwave_networkx as dnx
    from dwave.system import DWaveSampler
    from dwave.system.composites import EmbeddingComposite
    from dwave.system.package_info import __version__
    print("SUCCESSFULLY LOADED NETWORKX", __version__)
    return {'dwave_version': __version__, 'success': 'SUCCESSFULLY LOADED DWAVE', 'loading_time': time.time() - start_time}
