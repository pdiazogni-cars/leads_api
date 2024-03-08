import unittest
from typing import List

from pyramid import testing


class CoverageGetTests(unittest.TestCase):
    """Unit test for coverage view"""

    def test_ok(self):
        from leads_api.views.coverage import coverage_get

        # Query and path parameters
        parameters = DummyParameters(
            query={
                'zipcode': '10010',
            },
            path={
                'buyer_tier_slug': 'test-buyer-tier',
                'make_slug': 'honda',
            },
        )

        # Dummy data expected from query
        query_row = {
            'buyer': 'b1',
            'buyer_tier': 'b1-blind',
            'dealer_code': 'b1-dealer-a',
            'dealer_name': 'Dealer A',
            'dealer_address': 'St 123',
            'dealer_city': 'Los Angeles',
            'dealer_state': 'CA',
            'dealer_zipcode': '10020',
            'dealer_phone': '123-4567',
            'distance': 10,
            'zipcode': '10010',
            'make': 'honda',
        }
        # Creates dummy database objects
        query_result = [
            DummyRow(query_row)
        ]
        dbsession = DummyDBSession(query_result)

        # Dummy pyramid request
        request = testing.DummyRequest(
            params=parameters.query,
            openapi_validated=DummyValidated(parameters),
            dbsession=dbsession
        )

        # Run the view
        data = coverage_get(request)

        # Should include buyer info and `has_coverage`
        self.assertTrue(data.get('has_coverage'))
        for key in ('buyer', 'buyer_tier'):
            self.assertEqual(data.get(key), query_row[key])

        # There should be a coverage list with all the dealers info
        coverage = data.get('coverage')
        self.assertIsInstance(coverage, list)
        self.assertEqual(len(coverage), 1)
        row = coverage[0]

        # The row must contain the following keys, and values
        # should be the same as the ones from the dummy query object
        for key in (
            'dealer_code',
            'dealer_name',
            'dealer_address',
            'dealer_city',
            'dealer_state',
            'dealer_zipcode',
            'dealer_phone',
            'distance',
            'zipcode',
        ):
            self.assertEqual(row.get(key), query_row[key])


class DummyDBSession:
    """Dummy SQLAlchemy Session for testing"""

    def __init__(self, query_result: List['DummyRow']):
        """
        Args:
           query_result (List[DummyRow]): The dummy result for sesion.query().all() call
        """
        self.query_result = query_result

    def __call__(self, *args, **kwargs):
        """Always return self to create an inifinite mock until all() is called"""
        return self

    def __getattr__(self, attr):
        """Always return self to create an inifinite mock until all() is called"""
        if attr == 'all':
            return lambda: self.query_result
        else:
            return self


class DummyRow:
    """Dummy SQLAlchemy query() result object that wraps the actual data"""

    def __init__(self, row: dict):
        """
        Args:
            row (dict): The dummy data that will be returned.
        """
        self.row = row

    def _asdict(self):
        """Returns the actual row"""
        return self.row


class DummyValidated:

    def __init__(self, parameters):
        self.parameters = parameters


class DummyParameters:

    def __init__(self, query=None, path=None):
        self.query = query
        self.path = path
