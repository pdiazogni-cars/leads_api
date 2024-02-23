import sys
import yaml
import argparse
import logging
from pathlib import Path
from typing import Dict

from sqlalchemy import String, Integer, Table

from leads_api.models import tables

logger = logging.getLogger(__name__)

tables_by_name = vars(tables)


class BaseSQLGenerator:
    """Base class to parse buyers/dealers data from yaml file
    and generate SQL dumps for each table.

    This class is intended to be used as entry point of processing the entire
    yaml file, and to be subclassed for each table into its own subgenerator
    with customizable rules.

    The structure of generators and subgenerators are similar to a tree, so
    based on declared __subgenerators__ `column_key` attribute, it will create an instance
    of that subgenerator and use it to process the data for that key.

        countries: <-- CountrySQLGenerator
          canada:
            slug: canada
            name: canada
            abbr: CA
            states: <-- CountryStateSQLGenerator
              ab:
                slug: ab
                name: Alberta

    If there is any key on the yaml file that doesn't match the subgenerators `column_key`,
    it won't be processed.
    """

    # Key used to match the data to process with a subgenerator
    column_key: str = None
    # The table used by each subgenerator. Needed to fetch the columns
    table: Table = None
    # The foreign key column name on other tables. Used to pass the foreign key value
    # to the subgenerator with the expected key so the subgenerator can add the relational column.
    foreign_key: str = None
    # Used to translate columns names used on the yaml that might be different on tables
    column_map: Dict = {}

    # List of the subgenerators this generator is expecting to find
    __subgenerators__ = [
        'YearSQLGenerator',
        'CountrySQLGenerator',
        'MakeSQLGenerator',
        'BuyerSQLGenerator',
    ]

    def __init__(self, generators_map: Dict, parent_generator: 'BaseSQLGenerator' = None):
        """Creates the generator

        Args
        ----
        * generators_map (dict): A dictionary with GeneratorClassName -> GeneratorClass to match
            subgenerators and creates them based on the class name.
        * parent_generator (BaseSQLGenerator): The parent generator from where it was created.
        """
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

        # Each generator will call `extract_rows()` and store all the rows here.
        # Later, this rows will be used to generate the output SQL
        self.rows = []

    def process(self, data: Dict):
        """Entry point to start processing the data. This method will be called
        only once by the main generator.

        Args:
        ----
        * data (dict): The data to process taken from the yaml file
        """

        # Iterate over the data and match the expected keys with subgenerators
        # to process each and extract the rows we need to build the SQLs
        for key, _data in data.items():
            if key not in self.subgenerators:
                raise ValueError(
                    f"Cannot find matching SQLGenerator for key `{key}`"
                )
            generator = self.subgenerators[key]
            generator.extract_rows(_data)

    def transform_data(self, data):
        """Method to subclass to apply normalization on data depending on the model"""
        return data

    def make_subforeign_data(self, data_key: str, data_values: Dict, foreign_data: Dict):
        """Based on the data and previous foreign_data, creates the next foreign_data
        dictionary that will be used by subgenerators in order to fetch previous
        foreign keys values.

        Args:
        -----
        * data_key (str): This key is often the same as the slug of the row, but mostly is
            a visual reference when looking at the plain yaml. It could be use as the foregin
            key for some cases if no `slug` is defined on data_values.
        * data_values (dict): The raw row information. We will look for the `slug` column to
            get the foreign_key.
        * foreign_data (dict): Previous foreign_data dictionary with other foreign keys that
            are needed too. E.g: For `buyer_make_model_year` we need buyer, make, model
            and year foreign keys that come from each parent generator.

        Returns:
        --------
        A dictionary with previous foreign data plus the current generator foreign key value.
        E.g:
        If previous foreign_data was {'buyer_slug': 'Buyer1'}, this method used from within
        a dealer might return {'buyer_slug': 'Buyer1', 'dealer_code': 'Dealer0001'}

        """
        # If there is no foreign key, dismiss this and return the foreign data as it is.
        if self.foreign_key is None:
            return foreign_data
        else:
            # Creates a new foreign_data dictionary with current generator foreign key
            # and previous foreign_data
            return {
                self.foreign_key: self._extract_foreign_key_value(data_key, data_values),
                **foreign_data,
            }

    def _extract_foreign_key_value(self, data_key: str, data_values: Dict):
        """Method to decide how to get foreign_key data from current generator to be
        used on subgenerators"""
        return data_values.get('slug') or data_key

    def extract_rows(self, data: Dict, foreign_data: Dict = None):
        """Process the data that comes from the whole yaml file, or just specific
        parts of this data taken from a parent generator.

        This is the default yaml structure that we expect for most
        of the tables. Some tables might have specific cases
        key: <-- Used to match which generator it should use
          data_keyA: <-- Mostly for visual purposes, but could be used as primary key
                       if no slug column is present
            columnA1: valueA1
            columnA2: valueA2
            columnAN: valueAN
            subgenerator_key: <-- If is not a column, it's sub data that needs a subgenerator
              data_keyB:
                columnB1: valueB1

        This method process the data and creates rows depending on the matching table
        and its columns, and store it inside `self.rows` that will be used later to
        generate the SQL statements.

        Args:
        -----
        * data (dict): The data taken from the yaml file that should be processed. It could be
            the entire file, or just a specific section previously
            matched with the current generator by a parent generator.
        * foreign_data (dict): Data that comes from previous parents generators with the needed
            foreign_keys.
        """
        # Initialize foreign_data as a dict
        if foreign_data is None:
            foreign_data = {}

        # Create a map of column -> type used for converting values into the expected type.
        # Avoid subgenerators which are not columns
        self.column_types = {
            column.name: column.type
            for column in self.table.columns
            if column not in self.subgenerators
        }
        # Keep a list of columns to use as an index to create the rows
        # with positional values
        self.columns = list(self.column_types.keys())

        # Depending on the generator some rows will need to be transformed
        # from a list into a dictionary, or add other missing data
        data = self.transform_data(data)

        # Start processing the data
        for data_key, data_values in data.items():
            # Create an empty row with all the columns slots
            row = [None] * len(self.columns)

            # Build foreign keys values that will be needed by subgenerators
            subforeign_data = self.make_subforeign_data(
                data_key,
                data_values,
                foreign_data,
            )

            # Join the row data + the foreign data from parent generators
            for column, value in list(data_values.items()) + list(foreign_data.items()):
                # Apply any column translation needed
                column = self.column_map.get(column, column)
                # If it's column, fill the row on the column position with the value
                if column in self.columns:
                    column_ix = self.columns.index(column)
                    row[column_ix] = value
                # If it's not a column, it has to be a reference to another table and
                # it needs to be processed by a subgenerator
                elif column in self.subgenerators:
                    # For subgenerators we need the current model slug
                    subgenerator = self.subgenerators[column]
                    subgenerator.extract_rows(
                        value,
                        foreign_data=subforeign_data
                    )
                else:
                    raise ValueError(
                        f"Error on {self}: Unknown column `{column}` inside key "
                        f"`{self.column_key}`"
                    )
            self.rows.append(row)

    def get_sql(self):
        """Generates the SQL statement for current generator only

        Returns:
        --------
        A string with the SQL COPY statement with all processed rows.
        """
        # If there are no rows, then skip the statement
        if not self.rows:
            return ""

        # Process extracted rows and generate the SQL
        rows_new = []
        for row in self.rows:
            row_new = []
            for column_ix, value in enumerate(row):
                # Get the column using the index of each value
                column = self.columns[column_ix]
                column_type = self.column_types[column]
                # If the value is None, then just add an empty string
                if value is None:
                    row_new.append('')
                # If the value is String, surround it with quotes
                elif isinstance(column_type, (String,)):
                    row_new.append(f"'{value}'")
                # If the value is Integer, only convert it to string without quotes
                elif isinstance(column_type, (Integer,)):
                    row_new.append(str(value))
                else:
                    raise ValueError(f"Unsupported column type: {column_type}")
            # Append the string row line
            rows_new.append('(' + ', '.join(row_new) + ')')

        # Join columns and rows into text
        columns_str = ', '.join(self.columns)
        rows_str = '\n'.join(rows_new)

        # Generate the final SQL statement and return it
        copy_statement = (
            f"-- Data from table `self.table_name`\n"
            f"COPY {self.table.name} ({columns_str}) "
            f"FROM STDIN;\n{rows_str}\n\n"
        )
        return copy_statement

    def get_all_sql(self):
        """Create the current generator SQL statement and collect all the
        subgenerators SQL statements too, to return it to the parent generator.

        Returns:
        --------
        A string with all the SQL COPY statements generated by this generator and
        its subgenerators.
        """
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
    foreign_key = 'year_slug'

    def transform_data(self, data):
        """Years are represented as a list instead of a dict, so we need
        to do a transformation and add explicitly the year_slug column"""
        return {
            self.column_key: {
                self.foreign_key: x
                for x in data
            }
        }


class CountrySQLGenerator(BaseSQLGenerator):
    table = tables_by_name['country']
    column_key = 'countries'
    foreign_key = 'country_slug'
    __subgenerators__ = [
        'CountryStateSQLGenerator'
    ]


class CountryStateSQLGenerator(BaseSQLGenerator):
    table = tables_by_name['country_state']
    column_key = 'states'
    __subgenerators__ = []


class MakeSQLGenerator(BaseSQLGenerator):
    table = tables_by_name['make']
    column_key = 'makes'
    foreign_key = 'make_slug'
    __subgenerators__ = [
        'MakeYearSQLGenerator',
        'MakeModelSQLGenerator',
    ]


class MakeYearSQLGenerator(YearSQLSubgenerator):
    table = tables_by_name['make_year']


class MakeModelSQLGenerator(BaseSQLGenerator):
    table = tables_by_name['make_model']
    column_key = 'models'
    foreign_key = 'model_slug'
    __subgenerators__ = [
        'MakeModelYearSQLGenerator'
    ]


class MakeModelYearSQLGenerator(YearSQLSubgenerator):
    table = tables_by_name['make_model_year']


class BuyerSQLGenerator(BaseSQLGenerator):
    table = tables_by_name['buyer']
    column_key = 'buyers'
    foreign_key = 'buyer_slug'
    __subgenerators__ = [
        'BuyerYearSQLGenerator',
        'BuyerMakeSQLGenerator',
        'BuyerTierSQLGenerator',
        'BuyerDealerSQLGenerator',
    ]


class BuyerYearSQLGenerator(YearSQLSubgenerator):
    table = tables_by_name['buyer_year']


class ForeignKeySQLGenerator(BaseSQLGenerator):
    """Inherit by SQLGenerators that needs to add its own
    foreign key into the data.
    """

    def transform_data(self, data: Dict):
        """Recreates the data dictionary and uses
        the data_key as the current generator foreign key
        that might be missing on the data

        Args:
        -----
        * data (dict): The data to process that comes from the parent generator.

        Returns:
        --------
        The same data dict with the current generator foreign_key value within
        that will be needed too.
        """

        return {
            data_key: {
                self.foreign_key: data_key,
                **data[data_key]
            }
            for data_key in data
        }


class BuyerMakeSQLGenerator(ForeignKeySQLGenerator):
    table = tables_by_name['buyer_make']
    column_key = 'makes'
    foreign_key = 'make_slug'
    __subgenerators__ = [
        'BuyerMakeYearSQLGenerator',
        'BuyerMakeModelSQLGenerator',
    ]


class BuyerMakeYearSQLGenerator(YearSQLSubgenerator):
    table = tables_by_name['buyer_make_year']


class BuyerMakeModelSQLGenerator(ForeignKeySQLGenerator):
    table = tables_by_name['buyer_make_model']
    column_key = 'models'
    foreign_key = 'model_slug'
    __subgenerators__ = [
        'BuyerMakeModelYearSQLGenerator',
    ]


class BuyerMakeModelYearSQLGenerator(YearSQLSubgenerator):
    table = tables_by_name['buyer_make_model_year']


class BuyerTierSQLGenerator(BaseSQLGenerator):
    table = tables_by_name['buyer_tier']
    column_key = 'tiers'
    foreign_key = 'tier_slug'
    __subgenerators__ = [
        'LegacyBuyerTierSQLGenerator',
        'BuyerTierYearSQLGenerator',
        'BuyerTierMakeSQLGenerator',
    ]


class LegacyBuyerTierSQLGenerator(BaseSQLGenerator):
    table = tables_by_name['legacy_buyer_tier']
    column_key = 'legacy'
    column_map = {'tier_slug': 'buyer_tier_slug'}
    __subgenerators__ = []

    def transform_data(self, data: Dict):
        """For legacy data we need to do a name transformation
        and return it into a known format."""
        return {
            'legacy': {
                'legacy_id': data['id'],
                'legacy_name': data['name'],
            }
        }


class BuyerTierYearSQLGenerator(YearSQLSubgenerator):
    table = tables_by_name['buyer_tier_year']


class BuyerTierMakeSQLGenerator(BaseSQLGenerator):
    table = tables_by_name['buyer_tier_make']
    column_key = 'makes'
    foreign_key = 'make_slug'
    __subgenerators__ = [
        'BuyerTierMakeYearSQLGenerator',
        'BuyerTierMakeModelSQLGenerator',
    ]


class BuyerTierMakeYearSQLGenerator(YearSQLSubgenerator):
    table = tables_by_name['buyer_tier_make_year']


class BuyerTierMakeModelSQLGenerator(ForeignKeySQLGenerator):
    table = tables_by_name['buyer_tier_make_model']
    column_key = 'models'
    foreign_key = 'model_slug'
    __subgenerators__ = [
        'BuyerTierMakeModelYearSQLGenerator',
    ]


class BuyerTierMakeModelYearSQLGenerator(YearSQLSubgenerator):
    table = tables_by_name['buyer_tier_make_model_year']


class BuyerDealerSQLGenerator(BaseSQLGenerator):
    table = tables_by_name['buyer_dealer']
    column_key = 'dealers'
    foreign_key = 'dealer_code'

    __subgenerators__ = [
        'BuyerDealerYearSQLGenerator',
        'BuyerDealerMakeSQLGenerator',
    ]


class BuyerDealerYearSQLGenerator(YearSQLSubgenerator):
    table = tables_by_name['buyer_dealer_year']


class BuyerDealerMakeSQLGenerator(ForeignKeySQLGenerator):
    table = tables_by_name['buyer_dealer_make']
    column_key = 'makes'
    foreign_key = 'make_slug'
    __subgenerators__ = [
        'BuyerDealerMakeYearSQLGenerator',
        'BuyerDealerMakeModelSQLGenerator',
    ]


class BuyerDealerMakeYearSQLGenerator(YearSQLSubgenerator):
    table = tables_by_name['buyer_dealer_make_year']


class BuyerDealerMakeModelSQLGenerator(ForeignKeySQLGenerator):
    table = tables_by_name['buyer_dealer_make_model']
    column_key = 'models'
    foreign_key = 'model_slug'
    __subgenerators__ = [
        'BuyerDealerMakeModelYearSQLGenerator',
    ]


class BuyerDealerMakeModelYearSQLGenerator(YearSQLSubgenerator):
    table = tables_by_name['buyer_dealer_make_model_year']


# Once we have all the Generator classes defined, we
# need to group them in a list to create a map of available generators
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

# Map of class name -> generator class to be used to initiate them later
generators_map = {
    generator.__name__: generator
    for generator in generators
}


def main(source: Path, output: Path):
    """Loads the yaml file, create the SQL generators, process the rows and dumps
    the final output.

    Args:
    -----
    * source (Path): The yaml source file with the data that needs to be processed
    * output (Path): The path where the output SQL statements will be dumped
    """
    # Parse the yaml file into a dictionary of data
    with open(source, 'r') as f:
        data = yaml.safe_load(f)

    # Create the Main generator as the entrypoint of the whole process
    main_generator = BaseSQLGenerator(generators_map)

    # Extract all rows from the data
    main_generator.process(data)

    # Create final SQL statement
    sql = main_generator.get_all_sql()

    # Dump the results to the output
    output.write(sql)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('source', type=Path)
    ap.add_argument('-o', '--output', type=Path)
    args = ap.parse_args()
    try:
        # By default dump the results to stdout
        if args.output is None:
            args.output = sys.stdout
        else:
            args.output = open(args.output, 'w')

        # Start process
        main(args.source, args.output)
    finally:
        # Given we might use stdout, close manually instead of
        # using `with` statement
        args.output.close()
