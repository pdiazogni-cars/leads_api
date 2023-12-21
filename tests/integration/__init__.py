from webtest import TestApp
import unittest

import alembic
import alembic.config
import alembic.command
import transaction
from pyramid.paster import get_appsettings

from leads_api import main
from leads_api.models import get_tm_session, get_engine
from leads_api.models.meta import metadata as dbmetadata


class BaseIntegrationTest(unittest.TestCase):
    """
    Base integration TestCase with everything needed to fully test
    the API responses while also using the SQLAlchemy model, making
    sure everything is cleanup after test runs.

    Notice that we are using `addCleanup()` over `tearDown()` to make sure
    it's always called even if `setUp()` fails
    """

    def setUp(self):
        # Settings for both API config (with db credentials) and for Alembic
        # to create the database model needed for tests
        ini_file = 'testing.ini'
        settings = get_appsettings(ini_file)
        alembic_cfg = alembic.config.Config(ini_file)

        # Create a DB engine based on the settings
        dbengine = get_engine(settings)

        # Make sure to cleanup the database before and after running tests
        def dbcleanup():
            dbmetadata.drop_all(bind=dbengine)
            alembic.command.stamp(alembic_cfg, None, purge=True)

        dbcleanup()
        self.addCleanup(dbcleanup)

        # Run alembic migrations to create a fresh schema
        alembic.command.upgrade(alembic_cfg, "head")

        # Creates the Pyramid application with the settings and the dbengine
        app = main({}, dbengine=dbengine, **settings)

        # Configure a transaction manager to ensure the DB session is rollbacked
        # after each test
        self.tm = transaction.manager
        self.tm.begin()
        self.tm.doom()
        self.addCleanup(self.tm.abort)

        # Create a DB session hooked to the transaction manager,
        # to make sure changes are always rollbacked
        self.dbsession = get_tm_session(
            app.registry['dbsession_factory'],
            self.tm
        )

        # Create the TestApp used for making the requests to test
        # the endpoints:
        # response = self.testapp.get('GET', '/endpoint')
        self.testapp = TestApp(
            app,
            extra_environ={
                'HTTP_HOST': 'localhost:6543',
                'tm.active': True,
                'tm.manager': self.tm,
                'app.dbsession': self.dbsession,
            },
        )
