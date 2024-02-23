import sys
import yaml
import argparse
import logging
from pathlib import Path

from sqlalchemy import String, Integer

from leads_api.models import tables

logger = logging.getLogger(__name__)

tables_by_name = vars(tables)


class BaseSQLGenerator:
    column_key = None
    table = None
    __subgenerators__ = [
        'YearSQLGenerator',
        'CountrySQLGenerator',
        'MakeSQLGenerator',
        'BuyerSQLGenerator',
    ]

    def __init__(self, generators_map, parent_generator=None):
        # Store the parent generator for future references
        self.parent_generator = parent_generator

        # Initiate subgenerators and store them by `column_key`
        # so we can easily match the data key to a subgenerator
        self.subgenerators = {
            generators_map[name].column_key: generators_map[name](
                generators_map,
                parent_generator=self,
            )
            for name in self.__subgenerators__
        }
        self.rows = []

    def process(self, data):
        """Entry point to start processing the data"""

        for key, _data in data.items():
            if key not in self.subgenerators:
                raise ValueError(
                    f"Cannot find matching SQLGenerator for key `{key}`"
                )
            generator = self.subgenerators[key]
            generator.extract_rows(_data)

    def transform_data(self, data):
        return data

    def extract_rows(self, data, foreign_data=None):
        """
        This is the default yaml structure that we expect for most
        of the tables. Some tables might have specific cases
        key:
          data_key (for visual purpose only, ignored):
            column1: value1
            column2: value2
            columnN: valueN
        """
        if foreign_data is None:
            foreign_data = {}

        # Create a map of column -> type to use for generating the SQL
        # Avoid subgenerators which are not columns
        self.column_types = {
            column.name: column.type
            for column in self.table.columns
            if column not in self.subgenerators
        }
        self.columns = list(self.column_types.keys())

        # Depending on the generator some rows will need to be transformed
        # from a list into a dictionary
        data = self.transform_data(data)

        for data_key, data_values in data.items():
            # Create an empty row with all the columns slots
            row = [None] * len(self.columns)
            # Join the row data + the foreign data from parent generators
            for column, value in list(data_values.items()) + list(foreign_data.items()):
                # If it's column, fill the row on the column position with the value
                if column in self.columns:
                    column_ix = self.columns.index(column)
                    row[column_ix] = value
                # If it's not a column, it has to be a reference to another table and
                # it needs to be processed by a subgenerator
                elif column in self.subgenerators:
                    # For subgenerators we need the current model slug
                    # to use as the foreign key
                    foreign_key = data_values.get('slug', data_key) or None
                    subgenerator = self.subgenerators[column]
                    subgenerator.extract_rows(
                        value,
                        foreign_data=dict(
                            {subgenerator.foreign_key: foreign_key},
                            **foreign_data,
                        )
                    )
                else:
                    raise ValueError(
                        f"Error on {self}: Unknown column `{column}` inside key "
                        f"`{self.column_key}`"
                    )
            self.rows.append(row)

    def get_sql(self):
        if not self.rows:
            return ""

        rows_new = []
        for row in self.rows:
            row_new = []
            for column_ix, value in enumerate(row):
                column = self.columns[column_ix]
                column_type = self.column_types[column]
                if isinstance(column_type, (String,)):
                    row_new.append(f"'{value}'")
                elif isinstance(column_type, (Integer,)):
                    row_new.append(str(value))
                else:
                    raise ValueError(f"Unsupported column type: {column_type}")
            rows_new.append('(' + ', '.join(row_new) + ')')

        columns_str = ', '.join(self.columns)
        rows_str = '\n'.join(rows_new)

        copy_statement = (
            f"-- Data from table `self.table_name`\n"
            f"COPY {self.table.name} ({columns_str}) "
            f"FROM STDIN;\n{rows_str}\n\n"
        )
        return copy_statement

    def get_all_sql(self):
        sql = self.get_sql()

        for name, generator in self.subgenerators.items():
            sql += generator.get_all_sql()

        return sql

    def __repr__(self):
        return self.__class__.__name__


class YearSQLGenerator(BaseSQLGenerator):
    table = tables_by_name['year']
    column_key = 'years'
    __subgenerators__ = []


class YearSQLSubgenerator(YearSQLGenerator):
    """We need a specific subgenerator for years that handles lists
    and adds the `year_slug` column
    """

    def transform_data(self, data):
        """Years are represented as a list instead of a dict, so we need
        to do a transformation and add explicitly the year_slug column"""
        return {'years': {'year_slug': x for x in data}}


class CountrySQLGenerator(BaseSQLGenerator):
    table = tables_by_name['country']
    column_key = 'countries'
    __subgenerators__ = [
        'CountryStateSQLGenerator'
    ]


class CountryStateSQLGenerator(BaseSQLGenerator):
    table = tables_by_name['country_state']
    column_key = 'states'
    foreign_key = 'country_slug'
    __subgenerators__ = []


class MakeSQLGenerator(BaseSQLGenerator):
    table = tables_by_name['make']
    column_key = 'makes'
    __subgenerators__ = [
        'MakeYearSQLGenerator',
        'MakeModelSQLGenerator',
    ]


class MakeYearSQLGenerator(YearSQLSubgenerator):
    table = tables_by_name['make_year']
    foreign_key = 'make_slug'


class MakeModelSQLGenerator(BaseSQLGenerator):
    table = tables_by_name['make_model']
    column_key = 'models'
    foreign_key = 'make_slug'
    __subgenerators__ = [
        'MakeModelYearSQLGenerator'
    ]


class MakeModelYearSQLGenerator(YearSQLSubgenerator):
    table = tables_by_name['make_model_year']
    foreign_key = 'model_slug'


class BuyerSQLGenerator(BaseSQLGenerator):
    table = tables_by_name['buyer']
    column_key = 'buyers'
    __subgenerators__ = [
        'BuyerYearSQLGenerator',
        'BuyerMakeSQLGenerator',
        'BuyerTierSQLGenerator',
        'BuyerDealerSQLGenerator',
    ]


class BuyerYearSQLGenerator(YearSQLSubgenerator):
    table = tables_by_name['buyer_year']
    foreign_key = 'buyer_slug'


class BuyerMakeSQLGenerator(BaseSQLGenerator):
    table = tables_by_name['buyer_make']
    column_key = 'makes'
    foreign_key = 'buyer_slug'
    __subgenerators__ = [
        'BuyerMakeYearSQLGenerator',
        'BuyerMakeModelSQLGenerator',
    ]

    def transform_data(self, data):
        return {
            data_key: dict(
                data[data_key].items(),
                **{'make_slug': data_key}
            )
            for data_key in data
        }


class BuyerMakeYearSQLGenerator(YearSQLSubgenerator):
    table = tables_by_name['buyer_make_year']
    foreign_key = 'buyer_slug'


class BuyerMakeModelSQLGenerator(BaseSQLGenerator):
    table = tables_by_name['buyer_make_model']
    column_key = 'models'
    foreign_key = 'buyer_slug'
    __subgenerators__ = [
        'BuyerMakeModelYearSQLGenerator',
    ]


class BuyerMakeModelYearSQLGenerator(YearSQLSubgenerator):
    table = tables_by_name['buyer_make_model_year']
    foreign_key = 'buyer_slug'


class BuyerTierSQLGenerator(BaseSQLGenerator):
    table = tables_by_name['buyer_tier']
    column_key = 'tiers'
    foreign_key = 'buyer_slug'
    __subgenerators__ = [
        'LegacyBuyerTierSQLGenerator',
        'BuyerTierYearSQLGenerator',
        'BuyerTierMakeSQLGenerator',
    ]


class LegacyBuyerTierSQLGenerator(BaseSQLGenerator):
    table = tables_by_name['legacy_buyer_tier']
    column_key = 'legacy'
    foreign_key = 'buyer_tier_slug'
    __subgenerators__ = []

    def transform_data(self, data):
        return {
            'legacy': {
                'legacy_id': data['id'],
                'legacy_name': data['name'],
            }
        }


class BuyerTierYearSQLGenerator(YearSQLSubgenerator):
    table = tables_by_name['buyer_tier_year']
    foreign_key = 'buyer_slug'


class BuyerTierMakeSQLGenerator(BaseSQLGenerator):
    table = tables_by_name['buyer_tier_make']
    column_key = 'makes'
    foreign_key = 'buyer_slug'
    __subgenerators__ = [
        'BuyerTierMakeYearSQLGenerator',
        'BuyerTierMakeModelSQLGenerator',
    ]


class BuyerTierMakeYearSQLGenerator(YearSQLSubgenerator):
    table = tables_by_name['buyer_tier_make_year']
    foreign_key = 'buyer_slug'


class BuyerTierMakeModelSQLGenerator(BaseSQLGenerator):
    table = tables_by_name['buyer_tier_make_model']
    column_key = 'models'
    foreign_key = 'buyer_slug'
    __subgenerators__ = [
        'BuyerTierMakeModelYearSQLGenerator',
    ]


class BuyerTierMakeModelYearSQLGenerator(YearSQLSubgenerator):
    table = tables_by_name['buyer_tier_make_model_year']
    foreign_key = 'buyer_slug'


class BuyerDealerSQLGenerator(BaseSQLGenerator):
    table = tables_by_name['buyer_dealer']
    column_key = 'dealers'
    foreign_key = 'buyer_slug'
    __subgenerators__ = [
        'BuyerDealerYearSQLGenerator',
        'BuyerDealerMakeSQLGenerator',
    ]


class BuyerDealerYearSQLGenerator(YearSQLSubgenerator):
    table = tables_by_name['buyer_dealer_year']
    foreign_key = 'buyer_slug'


class BuyerDealerMakeSQLGenerator(BaseSQLGenerator):
    table = tables_by_name['buyer_dealer_make']
    column_key = 'makes'
    foreign_key = 'buyer_slug'
    __subgenerators__ = [
        'BuyerDealerMakeYearSQLGenerator',
        'BuyerDealerMakeModelSQLGenerator',
    ]


class BuyerDealerMakeYearSQLGenerator(YearSQLSubgenerator):
    table = tables_by_name['buyer_dealer_make_year']
    foreign_key = 'buyer_slug'


class BuyerDealerMakeModelSQLGenerator(BaseSQLGenerator):
    table = tables_by_name['buyer_dealer_make_model']
    column_key = 'models'
    foreign_key = 'buyer_slug'
    __subgenerators__ = [
        'BuyerDealerMakeModelYearSQLGenerator',
    ]


class BuyerDealerMakeModelYearSQLGenerator(YearSQLSubgenerator):
    table = tables_by_name['buyer_dealer_make_model_year']
    foreign_key = 'buyer_slug'


generators = [
    YearSQLGenerator,
    CountrySQLGenerator,
    CountryStateSQLGenerator,
    MakeSQLGenerator,
    MakeYearSQLGenerator,
    MakeModelSQLGenerator,
    MakeModelYearSQLGenerator,
    BuyerSQLGenerator,
    BuyerYearSQLGenerator,
    BuyerMakeSQLGenerator,
    BuyerMakeYearSQLGenerator,
    BuyerMakeModelSQLGenerator,
    BuyerMakeModelYearSQLGenerator,
    BuyerTierSQLGenerator,
    LegacyBuyerTierSQLGenerator,
    BuyerTierYearSQLGenerator,
    BuyerTierMakeSQLGenerator,
    BuyerTierMakeYearSQLGenerator,
    BuyerTierMakeModelSQLGenerator,
    BuyerTierMakeModelYearSQLGenerator,
    BuyerDealerSQLGenerator,
    BuyerDealerYearSQLGenerator,
    BuyerDealerMakeSQLGenerator,
    BuyerDealerMakeYearSQLGenerator,
    BuyerDealerMakeModelSQLGenerator,
    BuyerDealerMakeModelYearSQLGenerator,
]

generators_map = {
    generator.__name__: generator
    for generator in generators
}


def main(source: Path, output: Path):
    """Loads the yaml file, create the SQL generators, process the rows and dumps
    the final output.
    """
    with open(source, 'r') as f:
        data = yaml.safe_load(f)

    main_generator = BaseSQLGenerator(generators_map)

    main_generator.process(data)

    sql = main_generator.get_all_sql()

    output.write(sql)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('source', type=Path)
    ap.add_argument('-o', '--output', type=Path)
    args = ap.parse_args()
    try:
        if args.output is None:
            args.output = sys.stdin
        else:
            args.output = open(args.output, 'w')

        main(args.source, args.output)
    finally:
        args.output.close()
