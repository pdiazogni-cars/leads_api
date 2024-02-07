from pyramid.request import Request
from pyramid.view import view_config

from leads_api.models.leads import (
    Buyer,
    BuyerDealer,
    BuyerTier,
    BuyerTierMake,
    #BuyerTierMakeYear,
    BuyerTierDealerCoverage,
    Make,
    #Year,
)


@view_config(
    route_name='v1_buyers_tiers_makes_coverage',
    openapi=True,
    renderer='json',
)
def coverage_get(request: Request):
    """Gets the dealers coverage for a specific buyer, make within a zipcode"""
    # Get requests params
    params = request.openapi_validated.parameters
    limit = params.query.get('limit', 3)
    buyer_tier = params.path['buyer_tier_slug']
    make = params.path['make_slug']
    zipcode = params.query['zipcode']

    # Prepare the query
    query = (
        request.dbsession.query(
            Buyer.name.label('buyer'),
            BuyerTier.name.label('buyer_tier'),
            Make.name.label('make'),
            #Year.name.label('year'),
            BuyerDealer.code.label('dealer_code'),
            BuyerDealer.name.label('dealer_name'),
            BuyerDealer.address.label('dealer_address'),
            BuyerDealer.city.label('dealer_city'),
            BuyerDealer.state.label('dealer_state'),
            BuyerDealer.zipcode.label('dealer_zipcode'),
            BuyerDealer.phone.label('dealer_phone'),
            BuyerTierDealerCoverage.distance.label('distance'),
            BuyerTierDealerCoverage.zipcode.label('zipcode'),
        )
        .filter(
            # Joins
            BuyerTier.slug == BuyerTierMake.tier_slug,
            BuyerTier.buyer_slug == Buyer.slug,
            BuyerDealer.buyer_slug == Buyer.slug,
            BuyerTierMake.make_slug == Make.slug,
            #BuyerTierMakeYear.make_slug == Make.slug, # Enable this to add year filtering
            #BuyerTierMakeYear.year_slug == Year.slug, # Enable this to add year filtering
            BuyerTierDealerCoverage.buyer_tier_slug == BuyerTier.slug,
            # Filters
            BuyerTierMake.make_slug == make,
            BuyerTierMake.tier_slug == buyer_tier,
            BuyerTierDealerCoverage.zipcode == zipcode,
        )
        # Order result by distance ascending (we want the closer dealers)
        .order_by(BuyerTierDealerCoverage.distance)
        # Return only a limited amount of dealers. Initially, this number will be provided
        # by the client but later we could handle all the buyers configurations
        # and store this number in the database
        .limit(limit)
    )

    # Fetch all rows
    rows = query.all()

    # Parse results into the expected dict format:
    # {
    #   'status': status,
    #   'data': [
    #     'has_coverage': True/False,
    #     'buyer': buyer,
    #     'buyer_tier': buyer_tier,
    #     'coverage': [
    #        { dealer 1 info + coverage },
    #        { dealer 2 info + coverage },
    #     ]
    #   ],
    #   'metadata': request metadata,
    # }
    data = {}
    if len(rows) > 0:
        data['has_coverage'] = True
        row = rows[0]._asdict()
        data['buyer'] = row['buyer']
        data['buyer_tier'] = row['buyer_tier']
        data['coverage'] = []
        for row in rows:
            row = row._asdict()
            coverage = {
                'dealer_code': row['dealer_code'],
                'dealer_name': row['dealer_name'],
                'dealer_address': row['dealer_address'],
                'dealer_city': row['dealer_city'],
                'dealer_state': row['dealer_state'],
                'dealer_zipcode': row['dealer_zipcode'],
                'dealer_phone': row['dealer_phone'],
                'distance': row['distance'],
                'zipcode': row['zipcode'],
                'make': row['make'],
                #'year': row['year'],
            }
            data['coverage'].append(coverage)
    else:
        data['has_coverage'] = False

    return data
