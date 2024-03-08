import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'cornice',
    'marshmallow',
    'plaster_pastedeploy',
    'pyramid',
    'pyramid_jinja2',
    'pyramid_debugtoolbar',
    'waitress',
    'pyramid_retry',
    'pyramid_tm',
    'psycopg2',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
]

tests_require = [
    'WebTest',
    'pytest',
    'pytest-cov',
    'faker_boy',
    'parameterized',
]

setup(
    name='leads_api',
    version='0.0',
    description='leads_api',
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
