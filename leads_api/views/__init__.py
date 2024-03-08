from pyramid.request import Request
from pyramid.view import view_config


@view_config(name='response_wrapper')
def response_wrapper(request: Request):
    response = request.wrapped_response

    # Inject extra attributes into the response and move original
    # data inside 'data' key
    response.json = {
        'data': response.json,
        'metadata': {
            'params': dict(request.params),
        },
    }
    return response
