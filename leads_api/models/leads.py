"""
Core models which are shared with Obelisk, and populated via fixture data.
"""
from dataclasses import dataclass, field
from typing import List, Text
from sqlalchemy import (
    ForeignKey,
    Table,
    Column,
    Integer,
    String,
    UniqueConstraint,
    ForeignKeyConstraint,
)
from sqlalchemy.orm import relationship

from .meta import metadata, mapper_registry


__all__ = [
    'mapper_registry',
    'Make',
    'make',
    'MakeModel',
    'make_model',
    'Year',
    'year',
    'Buyer',
    'buyer',
    'BuyerTier',
    'buyer_tier',
    'LegacyBuyerTier',
    'legacy_buyer_tier',
    'BuyerDealer',
    'buyer_dealer',
    'BuyerDealerCoverage',
    'buyer_dealer_coverage',
    'make_year',
    'make_model_year',
    'buyer_make',
    'buyer_make_year',
    'buyer_tier_make',
    'buyer_tier_make_year',
    'buyer_dealer_make',
]


class JSONEncoder:
    def __json__(self, arg):
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }


@dataclass
class Year:
    slug: Text
    name: Text


@dataclass
class Make:
    slug: Text
    name: Text
    years: List['Year'] = field(default_factory=list)
    models: List['MakeModel'] = field(default_factory=list)


@dataclass
class MakeModel:
    make_slug: Text
    slug: Text
    name: Text
    years: List['Year'] = field(default_factory=list)


@dataclass
class Buyer:
    slug: Text
    name: Text
    makes: List['Make'] = field(default_factory=list)
    tiers: List['BuyerTier'] = field(default_factory=list)
    dealers: List['BuyerDealer'] = field(default_factory=list)


@dataclass
class BuyerTier:
    buyer_slug: Text
    slug: Text
    name: Text
    makes: List[Make] = field(default_factory=list)


@dataclass
class LegacyBuyerTier:
    buyer_slug: Text
    buyer_tier_slug: Text
    legacy_id: Integer
    legacy_name: Text


@dataclass
class BuyerDealer:
    buyer_slug: Text
    code: Text
    name: Text
    address: Text
    city: Text
    state: Text
    zipcode: Text
    phone: Text
    makes: List['Make'] = field(default_factory=list)
    coverage: List['BuyerDealerCoverage'] = field(default_factory=list)


@dataclass
class BuyerDealerCoverage:
    buyer_slug: Text
    buyer_dealer_code: Text
    zipcode: Text
    distance: int


@dataclass
class BuyerMake:
    buyer_slug: Text
    make_slug: Text


@dataclass
class BuyerTierMake:
    buyer_slug: Text
    tier_slug: Text
    make_slug: Text


@dataclass
class BuyerTierMakeYear:
    buyer_slug: Text
    tier_slug: Text
    make_slug: Text
    year_slug: Text


# ==== Tables ====

year = Table(
    'year',
    metadata,
    Column('slug', String(50), primary_key=True),
    Column('name', String(50), nullable=False),
    UniqueConstraint('name'),
)

make = Table(
    "make",
    metadata,
    Column("slug", String(50), primary_key=True),
    Column("name", String(50), nullable=False),
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
    "legacy_buyer_tier",
    metadata,
    Column("buyer_slug", String(50), primary_key=True),
    Column("buyer_tier_slug", String(50), primary_key=True),
    Column("legacy_id", Integer, nullable=False),
    Column("legacy_name", String(50), nullable=False),
    UniqueConstraint('legacy_id'),
    UniqueConstraint('legacy_name'),
    ForeignKeyConstraint(
        ["buyer_slug", "buyer_tier_slug"], ["buyer_tier.buyer_slug", "buyer_tier.slug"]
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
    Column('code', String(15), primary_key=True),
    Column('name', String(255)),
    Column('address', String(255)),
    Column('city', String(255)),
    Column('state', String(255)),
    Column('zipcode', String(255)),
    Column('phone', String(255)),
)

buyer_dealer_make = Table(
    'buyer_dealer_make',
    metadata,
    Column('buyer_slug', String(50), primary_key=True),
    Column('buyer_dealer_code', String(15), primary_key=True),
    Column('make_slug', String(50), primary_key=True),
    ForeignKeyConstraint(
        ['buyer_slug', 'buyer_dealer_code'],
        ['buyer_dealer.buyer_slug', 'buyer_dealer.code'],
    ),
    ForeignKeyConstraint(
        ['buyer_slug', 'make_slug'],
        ['buyer_make.buyer_slug', 'buyer_make.make_slug'],
    ),
)

buyer_dealer_coverage = Table(
    'buyer_dealer_coverage',
    metadata,
    Column('buyer_slug', String(50), primary_key=True),
    Column('buyer_dealer_code', String(50), primary_key=True),
    Column('zipcode', String(255), primary_key=True),
    Column('distance', Integer),
    ForeignKeyConstraint(
        ['buyer_slug', 'buyer_dealer_code'], ['buyer_dealer.buyer_slug', 'buyer_dealer.code']
    ),
)

# ========= Mappings ============
# Mappings should be done after declaring the Tables so
# we can build relationships between them

mapper_registry.map_imperatively(Year, year)

mapper_registry.map_imperatively(
    Make,
    make,
    properties={
        'years': relationship(Year, secondary=make_year),
        'models': relationship(MakeModel),
    }
)
mapper_registry.map_imperatively(
    MakeModel,
    make_model,
)

mapper_registry.map_imperatively(
    Buyer,
    buyer,
    properties={
        'makes': relationship(Make, secondary=buyer_make),
        'tiers': relationship(BuyerTier),
    }
)

mapper_registry.map_imperatively(
    BuyerTier,
    buyer_tier,
    properties={
        #'makes': relationship(Make, secondary=buyer_tier_make),
        'legacy_buyer_tier': relationship(
            LegacyBuyerTier,
            back_populates='buyer_tier',
            uselist=False,
        ),
    }
)

mapper_registry.map_imperatively(
    LegacyBuyerTier,
    legacy_buyer_tier,
    properties={
        'buyer_tier': relationship(
            BuyerTier,
            back_populates='legacy_buyer_tier',
            uselist=False,
        ),
    }
)

mapper_registry.map_imperatively(
    BuyerDealer,
    buyer_dealer,
    #properties={'makes': relationship(Make, secondary=buyer_dealer_make)},
)

mapper_registry.map_imperatively(
    BuyerDealerCoverage,
    buyer_dealer_coverage,
)

mapper_registry.map_imperatively(
    BuyerMake,
    buyer_make,
    #properties={
    #    'buyer': relationship(Buyer),
    #    'make': relationship(Make),
    #}
)

mapper_registry.map_imperatively(
    BuyerTierMake,
    buyer_tier_make,
    #properties={
    #    'buyer_tier': relationship(BuyerTier),
    #    'make': relationship(BuyerMake),
    #}
)

mapper_registry.map_imperatively(
    BuyerTierMakeYear,
    buyer_tier_make_year,
    #properties={
    #    'buyer': relationship(Buyer),
    #    'make': relationship(Make),
    #    'year': relationship(Year),
    #}
)
