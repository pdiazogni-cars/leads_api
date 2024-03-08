from pyramid.request import Request


def base_response_tween(handler, registry):
    """Tween wrapper to standarize all responses bodies after openapi3 modifications.
    We want to wrap all the responses to be a JSON dict containing some specific fields
    such as `metadata`.
    """

    def wrapper(request: Request):

        # Handle the request
        response = handler(request)

        # For any json response add metadata
        if response.content_type == 'application/json':
            former_response = response.json
            json_response = {
                'metadata': {
                    'params': dict(request.params),
                },
            }

            # If the request had an error, we want to return a document specifying
            # the list of errors
            if response.status_code < 400:
                json_response['data'] = former_response
            else:
                json_response['errors'] = former_response

            # Inject wrapped response
            response.json = json_response

        return response
    return wrapper


def includeme(config):
    config.add_tween('leads_api.tweens.base_response_tween')
