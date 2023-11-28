import factory

from leads_api.models.leads import (
    Buyer,
    BuyerTier,
    BuyerDealer,
    BuyerDealerCoverage,
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


class BuyerDealerCoverageFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = BuyerDealerCoverage

    # TODO: use factory.SubFactory
    buyer_slug = factory.Sequence(lambda n: f'buyer-{n}')
    buyer_dealer_code = factory.Sequence(lambda n: f'dealer-{n}')

    zipcode = factory.Faker('postcode')
    distance = factory.Faker('random_int', min=1, max=100)


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


def set_session(dbsession):
    for cls in [
        BuyerFactory,
        BuyerTierFactory,
        BuyerDealerFactory,
        BuyerDealerCoverageFactory,
        MakeFactory,
        BuyerMakeFactory,
        BuyerTierMakeFactory,
    ]:
        cls._meta.sqlalchemy_session_factory = lambda: dbsession
