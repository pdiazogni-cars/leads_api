from pyramid.request import Request
from marshmallow import Schema, fields
from cornice import Service
from cornice.validators import marshmallow_querystring_validator

from leads_api.models.leads import (
    Buyer,
    BuyerDealer,
    BuyerTier,
    BuyerTierMake,
    #BuyerTierMakeYear,
    BuyerDealerCoverage,
    Make,
    #Year,
)


class GetQuerystringSchema(Schema):
    buyer_tier = fields.String(required=True)
    zipcode = fields.String(required=True)
    make = fields.String(required=True)
    limit = fields.Integer(default=3)


coverage_service = Service(
    name='coverage',
    description="Returns the buyer's coverage of a make in a zipcode",
    pyramid_route='v1_coverage',
)


@coverage_service.get(
    schema=GetQuerystringSchema,
    validators=(marshmallow_querystring_validator),
)
def coverage_get(request: Request):
    # Get requests params
    limit = request.validated.get('limit', 3)
    buyer_tier = request.validated['buyer_tier']
    make = request.validated['make']
    zipcode = request.validated['zipcode']

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
            BuyerDealerCoverage.distance.label('distance'),
            BuyerDealerCoverage.zipcode.label('zipcode'),
        )
        .filter(
            # Joins
            BuyerTier.slug == BuyerTierMake.tier_slug,
            BuyerTier.buyer_slug == Buyer.slug,
            BuyerDealer.buyer_slug == Buyer.slug,
            BuyerTierMake.make_slug == Make.slug,
            #BuyerTierMakeYear.make_slug == Make.slug, # Enable this to add year filtering
            #BuyerTierMakeYear.year_slug == Year.slug, # Enable this to add year filtering
            BuyerDealerCoverage.buyer_dealer_code == BuyerDealer.code,
            # Filters
            BuyerTierMake.make_slug == make,
            BuyerTierMake.tier_slug == buyer_tier,
            BuyerDealerCoverage.zipcode == zipcode,
        )
        # Order result by distance ascending (we want the closer dealers)
        .order_by(BuyerDealerCoverage.distance)
        # Return only a limited amount of dealers. Initially, this number will be provided
        # by the client but later we could handle all the buyers configurations
        # and store this number in the database
        .limit(limit)
    )

    # Fetch all rows
    rows = query.all()

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

    result = {
        'status': 'ok',
        'data': data,
        'metadata': {
            'params': dict(request.params),
        },
    }
    return result
