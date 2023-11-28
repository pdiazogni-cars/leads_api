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


class CoverageGetTests(unittest.TestCase):

    def setUp(self):
        settings = get_appsettings('testing.ini')
        dbengine = get_engine(settings)
        alembic_cfg = alembic.config.Config('testing.ini')

        def dbcleanup():
            dbmetadata.drop_all(bind=dbengine)
            alembic.command.stamp(alembic_cfg, None, purge=True)

        self.dbcleanup = dbcleanup
        self.dbcleanup()
        alembic.command.upgrade(alembic_cfg, "head")

        app = main({}, dbengine=dbengine, **settings)
        self.tm = transaction.manager
        self.tm.begin()
        self.tm.doom()
        self.dbsession = get_tm_session(
            app.registry['dbsession_factory'],
            self.tm
        )
        self.testapp = TestApp(
            app,
            extra_environ={
                'HTTP_HOST': 'leads_api.com',
                'tm.active': True,
                'tm.manager': self.tm,
                'app.dbsession': self.dbsession,
            },
        )

    def tearDown(self):
        self.tm.abort()
        self.dbcleanup()

    def test_ok(self):
        from tests.integration.factories import (
            BuyerFactory,
            BuyerDealerFactory,
            BuyerMakeFactory,
            MakeFactory,
            BuyerTierFactory,
            BuyerDealerCoverageFactory,
            BuyerTierMakeFactory,
            set_session,
        )

        set_session(self.dbsession)

        make = MakeFactory()
        buyer = BuyerFactory()
        self.dbsession.flush()
        buyer_dealer = BuyerDealerFactory(buyer_slug=buyer.slug)
        buyer_tier = BuyerTierFactory(buyer_slug=buyer.slug)
        buyer_make = BuyerMakeFactory(
            buyer_slug=buyer.slug,
            make_slug=make.slug,
        )
        buyer_tier_make = BuyerTierMakeFactory(
            buyer_slug=buyer.slug,
            tier_slug=buyer_tier.slug,
            make_slug=make.slug,
        )
        dealer_coverage = BuyerDealerCoverageFactory(
            buyer_slug=buyer.slug,
            buyer_dealer_code=buyer_dealer.code
        )

        params = {
            'buyer_tier': buyer_tier.slug,
            'make': make.slug,
            'zipcode': dealer_coverage.zipcode,
        }

        response = self.testapp.get('/v1/coverage', params=params)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json.get('status'), 'ok')
        metadata = response.json.get('metadata')
        self.assertIsInstance(metadata, dict)
        self.assertEqual(metadata.get('params'), params)
        data = response.json.get('data')
        self.assertTrue(data.get('has_coverage'))
        self.assertEqual(data.get('buyer'), buyer.name)
        self.assertEqual(data.get('buyer_tier'), buyer_tier.name)
        coverage = data.get('coverage')
        self.assertIsInstance(coverage, list)
        self.assertEqual(len(coverage), 1)
        row = coverage[0]

        self.assertEqual(row.get('dealer_code'), buyer_dealer.code)
        self.assertEqual(row.get('dealer_name'), buyer_dealer.name)
        self.assertEqual(row.get('dealer_address'), buyer_dealer.address)
        self.assertEqual(row.get('dealer_city'), buyer_dealer.city)
        self.assertEqual(row.get('dealer_state'), buyer_dealer.state)
        self.assertEqual(row.get('dealer_zipcode'), buyer_dealer.zipcode)
        self.assertEqual(row.get('dealer_phone'), buyer_dealer.phone)
        self.assertEqual(row.get('distance'), dealer_coverage.distance)
        self.assertEqual(row.get('zipcode'), dealer_coverage.zipcode)
