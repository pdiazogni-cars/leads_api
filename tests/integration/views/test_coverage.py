from parameterized import parameterized

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
            BuyerTierDealerCoverageFactory,
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
        self.dealer_coverage = BuyerTierDealerCoverageFactory(
            buyer_tier_slug=self.buyer_tier.slug,
            dealer_code=self.buyer_dealer.code
        )

    def test_ok(self):
        """Test base coverage example"""

        # Creates dummy data
        self.make_one()

        # Sets requested params
        params = {
            'zipcode': self.dealer_coverage.zipcode,
        }

        # Performs the request for coverage
        response = self.testapp.get(
            f'/v1/buyers_tiers/{self.buyer_tier.slug}/makes/{self.make.slug}/coverage',
            params=params
        )

        # Should return OK status
        self.assertEqual(response.status_code, 200)

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

    @parameterized.expand(['zipcode'])
    def test_missing_params(self, remove_key):
        # Creates dummy data
        self.make_one()

        # Sets requested params
        params = {
            'zipcode': self.dealer_coverage.zipcode,
        }
        params.pop(remove_key)

        # Performs the request for coverage
        response = self.testapp.get(
            f'/v1/buyers_tiers/{self.buyer_tier.slug}/makes/{self.make.slug}/coverage',
            params=params,
            expect_errors=True,
        )

        # Should return 400 status
        self.assertEqual(response.status_code, 400)
        # Should have a list of errors with a single error
        errors = response.json.get('errors')
        self.assertIsInstance(errors, list)
        self.assertEqual(len(errors), 1)
        error = errors[0]
        # The error should be a MissingRequiredParameter and field should be the one we removed
        self.assertEqual(error.get('exception'), 'MissingRequiredParameter')
        self.assertEqual(error.get('field'), remove_key)
