# -*- coding: utf-8 -*-
"""
Contains the zip code model.
"""

from dataclasses import dataclass
from typing import Text

from sqlalchemy import (
    Column,
    String,
    Float,
    Table,
    select,
)
from geoalchemy2 import Geometry

from .meta import metadata, mapper_registry


zipcode = Table(
    'zip_code',
    metadata,
    Column('zip_code', String(50), primary_key=True),
    Column('city_name', String(50)),
    Column('county_name', String(50)),
    Column('state_name', String(50)),  # TODO: add foreign key state_slug
    Column('country_name', String(50)),  # TODO: add foreign key country_slug
    Column('msa', String(100)),
    Column('pmsa', String(100)),
    Column('latitude', Float(7, 4)),
    Column('longitude', Float(7, 4)),
    Column('geometry_point', Geometry("POINT", 4326))
)


@dataclass
class Zipcode:
    zip_code: Text
    city_name: Text
    county_name: Text
    state_name: Text
    country_name: Text
    msa: Text
    pmsa: Text
    latitude: float
    longitude: float
    geometry_point: Text


mapper_registry.map_imperatively(Zipcode, zipcode)


def get_zipcodes_around(dbsession, zipcode, distance):
    query = select(Zipcode.zip_code). \
        where(Zipcode.lat)
