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
from .tables import (
    year,
    country,
    country_state,
    make,
    make_year,
    make_model,
    make_model_year,
    buyer,
    buyer_year,
    buyer_make,
    buyer_make_year,
    buyer_make_model,
    buyer_make_model_year,
    buyer_tier,
    legacy_buyer_tier,
    buyer_tier_year,
    buyer_tier_make,
    buyer_tier_make_year,
    buyer_tier_make_model,
    buyer_tier_make_model_year,
    buyer_dealer,
    buyer_dealer_year,
    buyer_dealer_make,
    buyer_dealer_make_year,
    buyer_dealer_make_model,
    buyer_dealer_make_model_year,
    buyer_tier_dealer_coverage,
)


@dataclass
class Year:
    slug: Text
    name: Text


@dataclass
class Country:
    slug: Text
    name: Text
    abbr: Text
    states: List['CountryState'] = field(default_factory=list)


@dataclass
class CountryState:
    country_slug: Text
    slug: Text
    name: Text
    abbr: Text


@dataclass
class Make:
    slug: Text
    name: Text
    years: List['Year'] = field(default_factory=list)
    models: List['MakeModel'] = field(default_factory=list)


@dataclass
class MakeYear:
    make_slug: Text
    year_slug: Text


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


@dataclass
class BuyerTierDealerCoverage:
    buyer_tier_slug: Text
    dealer_code: Text
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


# ========= Mappings ============
# Mappings should be done after declaring the Tables so
# we can build relationships between them

mapper_registry.map_imperatively(Year, year)

mapper_registry.map_imperatively(
    Country,
    country,
    properties={
        'states': relationship(CountryState)
    }
)

mapper_registry.map_imperatively(CountryState, country_state)

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
    BuyerTierDealerCoverage,
    buyer_tier_dealer_coverage,
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
