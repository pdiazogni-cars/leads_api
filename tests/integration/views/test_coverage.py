from tests.integration import BaseIntegrationTest


class CoverageGetTests(BaseIntegrationTest):

    def make_one(self):
        """Creates the needed data to run the tests"""
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

        # FakerBoy models needs to be associated with the db session
        set_session(self.dbsession)

        # Create a make and a buyer, and flush it so they are available for
        # relations when creating the other models that include them as foreign keys
        self.make = MakeFactory()
        self.buyer = BuyerFactory()
        self.dbsession.flush()

        # Fill the other tables that depend on buyer and make
        self.buyer_dealer = BuyerDealerFactory(buyer_slug=self.buyer.slug)
        self.buyer_tier = BuyerTierFactory(buyer_slug=self.buyer.slug)
        self.buyer_make = BuyerMakeFactory(
            buyer_slug=self.buyer.slug,
            make_slug=self.make.slug,
        )
        self.buyer_tier_make = BuyerTierMakeFactory(
            buyer_slug=self.buyer.slug,
            tier_slug=self.buyer_tier.slug,
            make_slug=self.make.slug,
        )
        self.dealer_coverage = BuyerDealerCoverageFactory(
            buyer_slug=self.buyer.slug,
            buyer_dealer_code=self.buyer_dealer.code
        )

    def test_ok(self):
        """Test base coverage example"""

        # Creates dummy data
        self.make_one()

        # Sets requested params
        params = {
            'buyer_tier': self.buyer_tier.slug,
            'make': self.make.slug,
            'zipcode': self.dealer_coverage.zipcode,
        }

        # Performs the request for coverage
        response = self.testapp.get('/v1/coverage', params=params)

        # Should return OK status
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json.get('status'), 'ok')

        # Should include metadata with params
        metadata = response.json.get('metadata')
        self.assertIsInstance(metadata, dict)
        self.assertEqual(metadata.get('params'), params)

        # Should include the data with `has_coverage` flag and buyer info
        data = response.json.get('data')
        self.assertTrue(data.get('has_coverage'))
        self.assertEqual(data.get('buyer'), self.buyer.name)
        self.assertEqual(data.get('buyer_tier'), self.buyer_tier.name)

        # Should include `coverage` as a list with a single element (for this case)
        coverage = data.get('coverage')
        self.assertIsInstance(coverage, list)
        self.assertEqual(len(coverage), 1)
        row = coverage[0]

        # Coverage row should have the dealer and coverage info
        self.assertEqual(row.get('dealer_code'), self.buyer_dealer.code)
        self.assertEqual(row.get('dealer_name'), self.buyer_dealer.name)
        self.assertEqual(row.get('dealer_address'), self.buyer_dealer.address)
        self.assertEqual(row.get('dealer_city'), self.buyer_dealer.city)
        self.assertEqual(row.get('dealer_state'), self.buyer_dealer.state)
        self.assertEqual(row.get('dealer_zipcode'), self.buyer_dealer.zipcode)
        self.assertEqual(row.get('dealer_phone'), self.buyer_dealer.phone)
        self.assertEqual(row.get('distance'), self.dealer_coverage.distance)
        self.assertEqual(row.get('zipcode'), self.dealer_coverage.zipcode)
