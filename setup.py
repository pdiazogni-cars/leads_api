import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'openapi-core<0.17',
    'plaster_pastedeploy',
    'pyramid',
    'pyramid_jinja2',
    'pyramid_debugtoolbar',
    'pyramid_openapi3',
    'pyramid_retry',
    'pyramid_tm',
    'psycopg2',
    'SQLAlchemy',
    'transaction',
    'waitress',
    'zope.sqlalchemy',
]

tests_require = [
    'alembic',
    'WebTest',
    'pytest',
    'pytest-cov',
    'factory_boy',
    'parameterized',
]

setup(
    name='leads_api',
    version='1.0.0',
    description='Coverage generator API',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    author='',
    author_email='',
    url='',
    keywords='web pyramid pylons',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'testing': tests_require,
    },
    install_requires=requires,
    entry_points={
        'paste.app_factory': [
            'main = leads_api:main',
        ],
        'console_scripts': [
            'initialize_leads_api_db=leads_api.scripts.initialize_db:main',
        ],
    },
)
