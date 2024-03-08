"""
We use FactoryBoy module to map our current ORM models with
factory classes. Here we define the models and factories for each
column.
Note that each factory needs to be associated with the SQLAlchemy
session object.
"""
import factory

from leads_api.models.leads import (
    Buyer,
    BuyerTier,
    BuyerDealer,
    BuyerTierDealerCoverage,
    Make,
    BuyerMake,
    BuyerTierMake,
)


class BuyerFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Buyer

    name = factory.Sequence(lambda n: f'Buyer {n}')
    slug = factory.Sequence(lambda n: f'buyer-{n}')


class BuyerDealerFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = BuyerDealer

    # TODO: factory.SubFactory(BuyerFactory) is not working as expected,
    # because there is no way of map to the BuyerFactory.slug attribute.
    # This causes an error where instead of using the slug, uses the whole BuyerFactory object
    # as the buyer_slug.
    # buyer_slug = factory.SubFactory(BuyerFactory)
    buyer_slug = factory.Sequence(lambda n: f'buyer-{n}')

    code = factory.Sequence(lambda n: f'dealer-{n}')
    name = factory.Sequence(lambda n: f'Dealer {n}')
    address = factory.Faker('street_address')
    city = factory.Faker('city')
    state = factory.Faker('state')
    zipcode = factory.Faker('postcode')
    phone = factory.Faker('phone_number')


class MakeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Make

    name = factory.Iterator(['Honda', 'Mercedes-Benz', 'Toyota', 'Ford'])
    slug = factory.Iterator(['honda', 'mercedes-benz', 'toyota', 'ford'])


class BuyerMakeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = BuyerMake

    buyer_slug = factory.SubFactory(BuyerFactory)
    make_slug = factory.SubFactory(MakeFactory)

    # TODO: use factory.SubFactory
    buyer_slug = factory.Sequence(lambda n: f'buyer-{n}')
    make_slug = factory.Iterator(['honda', 'mercedes-benz', 'toyota', 'ford'])


class BuyerTierFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = BuyerTier

    # TODO: use factory.SubFactory
    buyer_slug = factory.Sequence(lambda n: f'buyer-{n}')

    name = factory.Sequence(lambda n: f'Buyer Tier {n}')
    slug = factory.Sequence(lambda n: f'buyer-tier-{n}')


class BuyerTierMakeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = BuyerTierMake

    # TODO: use factory.SubFactory
    buyer_slug = factory.Sequence(lambda n: f'buyer-{n}')
    tier_slug = factory.Sequence(lambda n: f'buyer-tier-{n}')
    make_slug = factory.Iterator(['honda', 'mercedes-benz', 'toyota', 'ford'])


class BuyerTierDealerCoverageFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = BuyerTierDealerCoverage

    # TODO: use factory.SubFactory
    buyer_tier_slug = factory.Sequence(lambda n: f'buyer-tier-{n}')
    dealer_code = factory.Sequence(lambda n: f'dealer-{n}')

    zipcode = factory.Faker('postcode')
    distance = factory.Faker('random_int', min=1, max=100)


def set_session(dbsession):
    """Associates all the factories models to the current testing db session.
    This way the factories can generate dummy data for testing in the same
    transaction and will be cleared later."""
    for cls in [
        BuyerFactory,
        BuyerTierFactory,
        BuyerDealerFactory,
        MakeFactory,
        BuyerMakeFactory,
        BuyerTierMakeFactory,
        BuyerTierDealerCoverageFactory,
    ]:
        cls._meta.sqlalchemy_session_factory = lambda: dbsession
