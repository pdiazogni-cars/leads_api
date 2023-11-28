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


make = Table(
    "make",
    metadata,
    Column("slug", String(50), primary_key=True),
    Column("name", String(50), nullable=False),
    UniqueConstraint('name'),
)


@dataclass
class Make:
    slug: Text
    name: Text
    years: List['Year'] = field(default_factory=list)
    models: List['MakeModel'] = field(default_factory=list)


make_model = Table(
    "make_model",
    metadata,
    Column("make_slug", String(50), ForeignKey("make.slug"), primary_key=True),
    Column("slug", String(50), primary_key=True),
    Column("name", String(50), nullable=False),
    UniqueConstraint('make_slug', 'name'),
)


@dataclass
class MakeModel:
    make_slug: Text
    slug: Text
    name: Text
    years: List['Year']


year = Table(
    "year",
    metadata,
    Column("slug", String(50), primary_key=True),
    Column("name", String(50), nullable=False),
    UniqueConstraint('name'),
    UniqueConstraint('slug'),
)


@dataclass
class Year:
    slug: Text
    name: Text


buyer = Table(
    "buyer",
    metadata,
    Column("slug", String(50), primary_key=True),
    Column("name", String(50), nullable=False),
    UniqueConstraint('name'),
    UniqueConstraint('slug'),
)


@dataclass
class Buyer(JSONEncoder):
    slug: Text
    name: Text
    #makes: List['Make']
    tiers: List['BuyerTier'] = field(default_factory=list)
    dealers: List['BuyerDealer'] = field(default_factory=list)


buyer_tier = Table(
    "buyer_tier",
    metadata,
    Column(
        "buyer_slug", String(50), ForeignKey("buyer.slug"), primary_key=True
    ),
    Column("slug", String(50), primary_key=True),
    Column("name", String(50), nullable=False),
    UniqueConstraint('buyer_slug', 'name'),
)


@dataclass
class BuyerTier(JSONEncoder):
    buyer_slug: Text
    slug: Text
    name: Text
    #makes: List[Make]


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


@dataclass
class LegacyBuyerTier:
    buyer_slug: Text
    buyer_tier_slug: Text
    legacy_id: Integer
    legacy_name: Text


buyer_dealer = Table(
    'buyer_dealer',
    metadata,
    Column(
        "buyer_slug", String(50), ForeignKey("buyer.slug"), primary_key=True
    ),
    Column('code', String(15), primary_key=True),
    Column('name', String(255)),
    Column('address', String(255)),
    Column('city', String(255)),
    Column('state', String(255)),
    Column('zipcode', String(255)),
    Column('phone', String(255)),
)


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
    #makes: List['Make']
    #coverage: List['BuyerDealerCoverage']


buyer_dealer_coverage = Table(
    'buyer_dealer_coverage',
    metadata,
    Column('buyer_slug', String(50), primary_key=True),
    Column('buyer_dealer_code', String(50), primary_key=True),
    Column('zipcode', String(255), primary_key=True),
    Column('distance', Integer),
    ForeignKeyConstraint(
        ["buyer_slug", "buyer_dealer_code"], ["buyer_dealer.buyer_slug", "buyer_dealer.code"]
    ),
)


@dataclass
class BuyerDealerCoverage:
    buyer_slug: Text
    buyer_dealer_code: Text
    zipcode: Text
    distance: int


# The tables defined below are association tables, and as such do not
# correspond to dataclass models.  Instead they will be mapped to
# attributes of the dataclasses as appropriate.


make_year = Table(
    'make_year',
    metadata,
    Column('make_slug', String(50), ForeignKey('make.slug'), primary_key=True),
    Column('year_slug', String(50), ForeignKey('year.slug'), primary_key=True),
)


make_model_year = Table(
    'make_model_year',
    metadata,
    Column('make_slug', String(50), primary_key=True),
    Column('model_slug', String(50), primary_key=True),
    Column('year_slug', String(50), primary_key=True),
    ForeignKeyConstraint(
        ["make_slug", "model_slug"], ["make_model.make_slug", "make_model.slug"]
    ),
    ForeignKeyConstraint(
        ["make_slug", "year_slug"], ["make_year.make_slug", "make_year.year_slug"]
    ),
)


buyer_make = Table(
    'buyer_make',
    metadata,
    Column(
        'buyer_slug', String(50), ForeignKey('buyer.slug'), primary_key=True
    ),
    Column('make_slug', String(50), ForeignKey('make.slug'), primary_key=True),
)


@dataclass
class BuyerMake(JSONEncoder):
    buyer_slug: Text
    make_slug: Text


buyer_make_year = Table(
    "buyer_make_year",
    metadata,
    Column('buyer_slug', String(50), primary_key=True),
    Column('make_slug', String(50), primary_key=True),
    Column('year_slug', String(50), primary_key=True),
    ForeignKeyConstraint(
        ["buyer_slug", "make_slug"],
        ["buyer_make.buyer_slug", "buyer_make.make_slug"],
    ),
    ForeignKeyConstraint(
        ["make_slug", "year_slug"],
        ["make_year.make_slug", "make_year.year_slug"],
    ),
)


buyer_tier_make = Table(
    'buyer_tier_make',
    metadata,
    Column('buyer_slug', String(50), primary_key=True),
    Column('tier_slug', String(50), primary_key=True),
    Column('make_slug', String(50), primary_key=True),
    ForeignKeyConstraint(
        ["buyer_slug", "tier_slug"], ["buyer_tier.buyer_slug", "buyer_tier.slug"]
    ),
    ForeignKeyConstraint(
        ["buyer_slug", "make_slug"],
        ["buyer_make.buyer_slug", "buyer_make.make_slug"],
    ),
)


@dataclass
class BuyerTierMake(JSONEncoder):
    buyer_slug: Text
    tier_slug: Text
    make_slug: Text


buyer_tier_make_year = Table(
    'buyer_tier_make_year',
    metadata,
    Column('buyer_slug', String(50), primary_key=True),
    Column('tier_slug', String(50), primary_key=True),
    Column('make_slug', String(50), primary_key=True),
    Column('year_slug', String(50), primary_key=True),
    ForeignKeyConstraint(
        ["buyer_slug", "tier_slug", "make_slug"],
        [
            "buyer_tier_make.buyer_slug",
            "buyer_tier_make.tier_slug",
            "buyer_tier_make.make_slug",
        ],
    ),
    ForeignKeyConstraint(
        ["buyer_slug", "make_slug", "year_slug"],
        [
            "buyer_make_year.buyer_slug",
            "buyer_make_year.make_slug",
            "buyer_make_year.year_slug",
        ],
    ),
)


@dataclass
class BuyerTierMakeYear(JSONEncoder):
    buyer_slug: Text
    tier_slug: Text
    make_slug: Text
    year_slug: Text


buyer_dealer_make = Table(
    'buyer_dealer_make',
    metadata,
    Column("buyer_slug", String(50), primary_key=True),
    Column('buyer_dealer_code', String(15), primary_key=True),
    Column('make_slug', String(50), primary_key=True),
    ForeignKeyConstraint(
        ["buyer_slug", "buyer_dealer_code"],
        ["buyer_dealer.buyer_slug", "buyer_dealer.code"],
    ),
    ForeignKeyConstraint(
        ["buyer_slug", "make_slug"],
        ["buyer_make.buyer_slug", "buyer_make.make_slug"],
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
        #'makes': relationship(Make, secondary=buyer_make),
        'tiers': relationship(BuyerTier),
    }
)

mapper_registry.map_imperatively(
    BuyerTier,
    buyer_tier,
    properties={
        #'makes': relationship(Make, secondary=buyer_tier_make),
        'legacy_buyer_tier': relationship(LegacyBuyerTier, back_populates='buyer_tier', uselist=False),
    }
)

mapper_registry.map_imperatively(
    LegacyBuyerTier,
    legacy_buyer_tier,
    properties={
        'buyer_tier': relationship(BuyerTier, back_populates='legacy_buyer_tier', uselist=False),
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

# TODO: Can we unify this with the above table?
mapper_registry.map_imperatively(
    BuyerTierMakeYear,
    buyer_tier_make_year,
    #properties={
    #    'buyer': relationship(Buyer),
    #    'make': relationship(Make),
    #    'year': relationship(Year),
    #}
)
