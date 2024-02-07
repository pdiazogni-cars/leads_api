from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    ForeignKey,
    UniqueConstraint,
    ForeignKeyConstraint,
)

from .meta import metadata

year = Table(
    'year',
    metadata,
    Column('slug', String(50), primary_key=True),
    Column('name', String(50), nullable=False),
    UniqueConstraint('name'),
)

country = Table(
    'country',
    metadata,
    Column('slug', String(50), primary_key=True),
    Column('name', String(50), nullable=False),
    Column('abbr', String(50), nullable=False),
    UniqueConstraint('name'),
    UniqueConstraint('abbr'),
)

country_state = Table(
    'country_state',
    metadata,
    Column('country_slug', String(50), ForeignKey('country.slug'), primary_key=True),
    Column('slug', String(50), primary_key=True),
    Column('name', String(50), nullable=False),
    Column('abbr', String(50), nullable=False),
    UniqueConstraint('country_slug', 'name'),
    UniqueConstraint('country_slug', 'abbr'),
)

make = Table(
    'make',
    metadata,
    Column('slug', String(50), primary_key=True),
    Column('name', String(50), nullable=False),
    UniqueConstraint('name'),
)

make_year = Table(
    'make_year',
    metadata,
    Column('make_slug', String(50), ForeignKey('make.slug'), primary_key=True),
    Column('year_slug', String(50), ForeignKey('year.slug'), primary_key=True),
)

make_model = Table(
    'make_model',
    metadata,
    Column('make_slug', String(50), ForeignKey('make.slug'), primary_key=True),
    Column('slug', String(50), primary_key=True),
    Column('name', String(50), nullable=False),
    UniqueConstraint('make_slug', 'name'),
)

make_model_year = Table(
    'make_model_year',
    metadata,
    Column('make_slug', String(50), primary_key=True),
    Column('model_slug', String(50), primary_key=True),
    Column('year_slug', String(50), primary_key=True),
    #Column('name', String(255), nullable=False),
    ForeignKeyConstraint(
        ['make_slug', 'model_slug'], ['make_model.make_slug', 'make_model.slug']
    ),
    ForeignKeyConstraint(
        ['make_slug', 'year_slug'], ['make_year.make_slug', 'make_year.year_slug']
    ),
)

buyer = Table(
    'buyer',
    metadata,
    Column('slug', String(50), primary_key=True),
    Column('name', String(50), nullable=False),
    UniqueConstraint('name'),
)

buyer_year = Table(
    'buyer_year',
    metadata,
    Column('buyer_slug', String(50), ForeignKey('buyer.slug'), primary_key=True),
    Column('year_slug', String(50), ForeignKey('year.slug'), primary_key=True),
)

buyer_make = Table(
    'buyer_make',
    metadata,
    Column('buyer_slug', String(50), ForeignKey('buyer.slug'), primary_key=True),
    Column('make_slug', String(50), ForeignKey('make.slug'), primary_key=True),
)

buyer_make_year = Table(
    'buyer_make_year',
    metadata,
    Column('buyer_slug', String(50), primary_key=True),
    Column('make_slug', String(50), primary_key=True),
    Column('year_slug', String(50), primary_key=True),
    ForeignKeyConstraint(
        ['buyer_slug', 'make_slug'],
        ['buyer_make.buyer_slug', 'buyer_make.make_slug'],
    ),
    ForeignKeyConstraint(
        ['make_slug', 'year_slug'],
        ['make_year.make_slug', 'make_year.year_slug'],
    ),
)

buyer_make_model = Table(
    'buyer_make_model',
    metadata,
    Column('buyer_slug', String(50), ForeignKey('buyer.slug'), primary_key=True),
    Column('make_slug', String(50), primary_key=True),
    Column('model_slug', String(50), primary_key=True),
    ForeignKeyConstraint(
        ['buyer_slug', 'make_slug'], ['buyer_make.buyer_slug', 'buyer_make.make_slug']
    ),
    ForeignKeyConstraint(
        ['make_slug', 'model_slug'], ['make_model.make_slug', 'make_model.slug']
    ),
)

buyer_make_model_year = Table(
    'buyer_make_model_year',
    metadata,
    Column('buyer_slug', String(50), primary_key=True),
    Column('make_slug', String(50), primary_key=True),
    Column('model_slug', String(50), primary_key=True),
    Column('year_slug', String(50), primary_key=True),
    ForeignKeyConstraint(
        ['buyer_slug', 'make_slug', 'model_slug'],
        ['buyer_make_model.buyer_slug', 'buyer_make_model.make_slug', 'buyer_make_model.model_slug'],
    ),
    ForeignKeyConstraint(
        ['buyer_slug', 'make_slug', 'year_slug'],
        ['buyer_make_year.buyer_slug', 'buyer_make_year.make_slug', 'buyer_make_year.year_slug'],
    ),
)

buyer_tier = Table(
    'buyer_tier',
    metadata,
    Column(
        'buyer_slug', String(50), ForeignKey('buyer.slug'), primary_key=True
    ),
    Column('slug', String(50), primary_key=True),
    Column('name', String(50), nullable=False),
    UniqueConstraint('buyer_slug', 'name'),
)

legacy_buyer_tier = Table(
    'legacy_buyer_tier',
    metadata,
    Column('buyer_slug', String(50), primary_key=True),
    Column('buyer_tier_slug', String(50), primary_key=True),
    Column('legacy_id', Integer, nullable=False),
    Column('legacy_name', String(50), nullable=False),
    UniqueConstraint('legacy_id'),
    UniqueConstraint('legacy_name'),
    ForeignKeyConstraint(
        ['buyer_slug', 'buyer_tier_slug'], ['buyer_tier.buyer_slug', 'buyer_tier.slug']
    ),
)

buyer_tier_year = Table(
    'buyer_tier_year',
    metadata,
    Column('buyer_slug', String(50), primary_key=True),
    Column('tier_slug', String(50), primary_key=True),
    Column('year_slug', String(50), primary_key=True),
    ForeignKeyConstraint(
        ['buyer_slug', 'tier_slug'], ['buyer_tier.buyer_slug', 'buyer_tier.slug'],
    ),
    ForeignKeyConstraint(
        ['buyer_slug', 'year_slug'], ['buyer_year.buyer_slug', 'buyer_year.year_slug'],
    ),
)

buyer_tier_make = Table(
    'buyer_tier_make',
    metadata,
    Column('buyer_slug', String(50), primary_key=True),
    Column('tier_slug', String(50), primary_key=True),
    Column('make_slug', String(50), primary_key=True),
    ForeignKeyConstraint(
        ['buyer_slug', 'tier_slug'], ['buyer_tier.buyer_slug', 'buyer_tier.slug']
    ),
    ForeignKeyConstraint(
        ['buyer_slug', 'make_slug'],
        ['buyer_make.buyer_slug', 'buyer_make.make_slug'],
    ),
)


buyer_tier_make_year = Table(
    'buyer_tier_make_year',
    metadata,
    Column('buyer_slug', String(50), primary_key=True),
    Column('tier_slug', String(50), primary_key=True),
    Column('make_slug', String(50), primary_key=True),
    Column('year_slug', String(50), primary_key=True),
    ForeignKeyConstraint(
        ['buyer_slug', 'tier_slug', 'make_slug'],
        [
            'buyer_tier_make.buyer_slug',
            'buyer_tier_make.tier_slug',
            'buyer_tier_make.make_slug',
        ],
    ),
    ForeignKeyConstraint(
        ['buyer_slug', 'tier_slug', 'year_slug'],
        [
            'buyer_tier_year.buyer_slug',
            'buyer_tier_year.tier_slug',
            'buyer_tier_year.year_slug',
        ],
    ),
)

buyer_tier_make_model = Table(
    'buyer_tier_make_model',
    metadata,
    Column('buyer_slug', String(50), primary_key=True),
    Column('tier_slug', String(50), primary_key=True),
    Column('make_slug', String(50), primary_key=True),
    Column('model_slug', String(50), primary_key=True),
    ForeignKeyConstraint(
        ['buyer_slug', 'tier_slug', 'make_slug'],
        [
            'buyer_tier_make.buyer_slug',
            'buyer_tier_make.tier_slug',
            'buyer_tier_make.make_slug',
        ],
    ),
    ForeignKeyConstraint(
        ['buyer_slug', 'make_slug', 'model_slug'],
        [
            'buyer_make_model.buyer_slug',
            'buyer_make_model.make_slug',
            'buyer_make_model.model_slug',
        ],
    ),
)

buyer_tier_make_model_year = Table(
    'buyer_tier_make_model_year',
    metadata,
    Column('buyer_slug', String(50), primary_key=True),
    Column('tier_slug', String(50), primary_key=True),
    Column('make_slug', String(50), primary_key=True),
    Column('model_slug', String(50), primary_key=True),
    Column('year_slug', String(50), primary_key=True),
    ForeignKeyConstraint(
        ['buyer_slug', 'tier_slug', 'make_slug', 'model_slug'],
        [
            'buyer_tier_make_model.buyer_slug',
            'buyer_tier_make_model.tier_slug',
            'buyer_tier_make_model.make_slug',
            'buyer_tier_make_model.model_slug',
        ],
    ),
    ForeignKeyConstraint(
        ['buyer_slug', 'tier_slug', 'make_slug', 'year_slug'],
        [
            'buyer_tier_make_year.buyer_slug',
            'buyer_tier_make_year.tier_slug',
            'buyer_tier_make_year.make_slug',
            'buyer_tier_make_year.year_slug',
        ],
    ),
)

buyer_dealer = Table(
    'buyer_dealer',
    metadata,
    Column(
        'buyer_slug', String(50), ForeignKey('buyer.slug'), primary_key=True
    ),
    Column('code', String(50), primary_key=True),
    Column('name', String(255)),
    Column('address', String(255)),
    Column('city', String(255)),
    Column('state', String(50)),
    Column('zipcode', String(255)),
    Column('country_slug', String(50)),
    Column('phone', String(255)),
    UniqueConstraint('buyer_slug', 'name', 'address', 'city', 'state', 'zipcode'),
    ForeignKeyConstraint(
        ['country_slug', 'state'],
        ['country_state.country_slug', 'country_state.abbr']
    ),
)

buyer_dealer_year = Table(
    'buyer_dealer_year',
    metadata,
    Column('buyer_slug', String(50), primary_key=True),
    Column('dealer_code', String(50), primary_key=True),
    Column('year_slug', String(50), primary_key=True),
    ForeignKeyConstraint(
        ['buyer_slug', 'dealer_code'],
        ['buyer_dealer.buyer_slug', 'buyer_dealer.code'],
    ),
    ForeignKeyConstraint(
        ['buyer_slug', 'year_slug'],
        ['buyer_year.buyer_slug', 'buyer_year.year_slug'],
    ),
)

buyer_dealer_make = Table(
    'buyer_dealer_make',
    metadata,
    Column('buyer_slug', String(50), primary_key=True),
    Column('dealer_code', String(50), primary_key=True),
    Column('make_slug', String(50), primary_key=True),
    ForeignKeyConstraint(
        ['buyer_slug', 'dealer_code'],
        ['buyer_dealer.buyer_slug', 'buyer_dealer.code'],
    ),
    ForeignKeyConstraint(
        ['buyer_slug', 'make_slug'],
        ['buyer_make.buyer_slug', 'buyer_make.make_slug'],
    ),
)

buyer_dealer_make_year = Table(
    'buyer_dealer_make_year',
    metadata,
    Column('buyer_slug', String(50), primary_key=True),
    Column('dealer_code', String(50), primary_key=True),
    Column('make_slug', String(50), primary_key=True),
    Column('year_slug', String(50), primary_key=True),
    ForeignKeyConstraint(
        ['buyer_slug', 'dealer_code', 'make_slug'],
        [
            'buyer_dealer_make.buyer_slug',
            'buyer_dealer_make.dealer_code',
            'buyer_dealer_make.make_slug',
        ],
    ),
    ForeignKeyConstraint(
        ['buyer_slug', 'dealer_code', 'year_slug'],
        [
            'buyer_dealer_year.buyer_slug',
            'buyer_dealer_year.dealer_code',
            'buyer_dealer_year.year_slug',
        ],
    ),
)

buyer_dealer_make_model = Table(
    'buyer_dealer_make_model',
    metadata,
    Column('buyer_slug', String(50), primary_key=True),
    Column('dealer_code', String(50), primary_key=True),
    Column('make_slug', String(50), primary_key=True),
    Column('model_slug', String(50), primary_key=True),
    ForeignKeyConstraint(
        ['buyer_slug', 'dealer_code', 'make_slug'],
        ['buyer_dealer_make.buyer_slug', 'buyer_dealer_make.dealer_code', 'buyer_dealer_make.make_slug'],
    ),
    ForeignKeyConstraint(
        ['buyer_slug', 'make_slug', 'model_slug'],
        ['buyer_make_model.buyer_slug', 'buyer_make_model.make_slug', 'buyer_make_model.model_slug'],
    ),
)

buyer_dealer_make_model_year = Table(
    'buyer_dealer_make_model_year',
    metadata,
    Column('buyer_slug', String(50), primary_key=True),
    Column('dealer_code', String(50), primary_key=True),
    Column('make_slug', String(50), primary_key=True),
    Column('model_slug', String(50), primary_key=True),
    Column('year_slug', String(50), primary_key=True),
    ForeignKeyConstraint(
        ['buyer_slug', 'dealer_code', 'make_slug', 'model_slug'],
        ['buyer_dealer_make_model.buyer_slug', 'buyer_dealer_make_model.dealer_code', 'buyer_dealer_make_model.make_slug', 'buyer_dealer_make_model.model_slug'],
    ),
    ForeignKeyConstraint(
        ['buyer_slug', 'dealer_code', 'make_slug', 'year_slug'],
        ['buyer_dealer_make_year.buyer_slug', 'buyer_dealer_make_year.dealer_code', 'buyer_dealer_make_year.make_slug', 'buyer_dealer_make_year.year_slug'],
    ),
)

buyer_tier_dealer_coverage = Table(
    'buyer_tier_dealer_coverage',
    metadata,
    Column('buyer_tier_slug', String(50), primary_key=True),
    Column('dealer_code', String(50), primary_key=True),
    Column('zipcode', String(255), primary_key=True),
    Column('distance', Integer),
    # TODO: Add foreign key constraints
)
