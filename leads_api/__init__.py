from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    with Configurator(settings=settings) as config:
        config.include('pyramid_jinja2')
        config.include('pyramid_openapi3')
        config.pyramid_openapi3_spec('openapi.yaml', route='/v1/openapi.yaml')
        config.pyramid_openapi3_add_explorer()
        config.include('.routes')
        config.include('.models')
        config.include('.tweens')
        config.scan(".views")
    return config.make_wsgi_app()
