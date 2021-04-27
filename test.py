from flask import request

with app.test_request_context('/api/skyquest/save/2376473', method='POST'):
    # now you can do something with the request until the
    # end of the with block, such as basic assertions:
    assert request.path == '/api/skyquest/save/2376473'
    assert request.method == 'POST'
