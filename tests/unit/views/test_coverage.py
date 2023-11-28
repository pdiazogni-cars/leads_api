import unittest
from pyramid import testing


class CoverageGetTests(unittest.TestCase):

    def setUp(self):
        self.default_params = {
            'buyer_tier': 'test-buyer-tier',
            'make': 'honda',
            'zipcode': '10010',
        }

    def test_ok(self):
        from leads_api.views.coverage import coverage_get
        params = self.default_params.copy()
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
        query_result = [
            DummyRow(query_row)
        ]
        dbsession = DummyDBSession(query_result)
        request = testing.DummyRequest(
            params=params,
            validated=params,
            dbsession=dbsession
        )

        response = coverage_get(request)

        self.assertIsInstance(response, dict)
        self.assertEqual(response.get('status'), 'ok')
        metadata = response.get('metadata')
        self.assertIsInstance(metadata, dict)
        self.assertEqual(metadata.get('params'), params)
        data = response.get('data')
        self.assertTrue(data.get('has_coverage'))
        for key in ('buyer', 'buyer_tier'):
            self.assertEqual(data.get(key), query_row[key])
        coverage = data.get('coverage')
        self.assertIsInstance(coverage, list)
        self.assertEqual(len(coverage), 1)
        row = coverage[0]

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

    def __init__(self, query_result):
        self.query_result = query_result

    def __call__(self, *args, **kwargs):
        return self

    def __getattr__(self, attr):
        if attr == 'all':
            return lambda: self.query_result
        else:
            return self


class DummyRow:

    def __init__(self, row):
        self.row = row

    def _asdict(self):
        return self.row
