def get_test_params(context):
    """Get parameters from test context regardless of scope"""
    params = {}

    if hasattr(context.request.node, 'callspec'):
        params = context.request.node.callspec.params
    elif context.request.node.get_closest_marker('parametrize'):
        marker = context.request.node.get_closest_marker('parametrize')
        params = dict(zip(marker.args[::2], marker.args[1::2][0]))

    return params