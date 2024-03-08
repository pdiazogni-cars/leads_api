import sys
from typing import List, Tuple, Text, Dict, Optional
from pathlib import Path

from sqlalchemy.schema import CreateTable

from leads_api.models.zipcode import zipcode as zipcode_table


class MelissaZipParser:

    # Taken from zag.ini melissa.zip.fields config
    fields_size_map = {
        'zip_code': 5,
        'state': 2,
        'city': 28,
        '_type': 1,
        'county_fips': 5,
        'latitude': 7,
        'longitude': 8,
        '_area_code': 3,
        '_finance_code': 6,
        'last_line': 1,
        '_fac': 1,
        'msa': 4,
        'pmsa': 4,
        '_filler': 3,
    }

    def __init__(self):
        self.fields = self.prep_fields(self.fields_size_map)
        self.skip_rows = 2  # Taken from zag.ini config
        self.row_length = max((x[2] for x in self.fields))

    def process(self, lines):
        for i, row in enumerate(lines[self.skip_rows:]):
            if not self.is_valid_row(row):
                raise ValueError(
                    f"Field spec '{self.fields}' is too long for row {row}"
                )
            else:
                fields = self.get_fields(row)
                result = self.to_model(fields)
                if result is not None:
                    yield result
                else:
                    pass
                    #print(f"Got empty result for row {i}")

    def is_valid_row(self, row: Text) -> bool:
        """
        We're only going to grab the parts of the row defined by the fields used in
        ``row_length``, so it's ok if the row is larger
        (it might have trailing or newline characters we don't care about).
        However, if the row is smaller than our row_length, parsing will
        fail when we try to access indices that don't exist.
        """
        return len(row) >= self.row_length

    def prep_fields(self, fields_size_map):
        """
        This is kind of an odd use case, but to support easier configuration (e.g.
        the "zip" field is 5 characters long, or ``[("zip", 5)]``), this helper
        will convert it to ``[("zip", 0, 5)]`` so we can index "95111"[0:5] and know
        that field's name is "zip".
        """
        result: List[Tuple[Text, int, int]] = []
        start = 0
        for (name, length) in fields_size_map.items():
            end = start + length
            if not name.startswith('_'):
                result.append((name, start, end))
            start += length
        return result

    def get_fields(self, row: Text) -> Dict[Text, Optional[Text]]:
        """
        This will create a mapping of field names to values (based on the provided
        ``fields_list`` config) for a given row. For the values, extra spaces
        are stripped and empty strings are converted to ``None``. This is an opinionated
        choice that best matches our use case, which is providing values to a model.
        Our models need to know if no value was found so that they can raise an exception
        or store ``null`` in the database, and there's no value to having all of them strip
        extra spaces when it's our only current use case.

        Any of these things can be made optional in the future if needed.
        """
        items: Dict[Text, Optional[Text]] = {}
        for (name, start, end) in self.fields:
            item = row[start:end].rstrip()
            items[name] = item if item != '' else None
        return items

    def to_model(self, d):
        if d['last_line'] != 'L':
            return None

        # next we ensure non-nullable fields are present
        zip_code = d['zip_code']
        state = d['state']
        city = d['city']

        if (
            zip_code is None
            or state is None
            or city is None
            or d['latitude'] is None
            or d['longitude'] is None
        ):
            raise ValueError(
                f"Zip code {zip_code} in {city}, {state} is not a valid zip"
            )
        # and finally we build the model. the ``float()`` conversion here is
        # not checked, but we trust melissa data to give us valid floats
        # (if not, re-run zag with ``--pdb`` to jump right in!)
        else:
            return (
                zip_code,
                state,
                city,
                d['county_fips'],
                float(d['latitude']),
                float(d['longitude']),
                d['msa'],
                d['pmsa'],
            )


def main(source: Path, output: Path):
    zipcode_table_path = f"{zipcode_table.schema}.{zipcode_table.name}"

    # Create PostGIS extension if not exist
    output.write("CREATE EXTENSION PostGIS;\n\n")

    # Drop and recreate zipcode table
    output.write(f"DROP TABLE {zipcode_table_path};\n\n")
    output.write(str(CreateTable(zipcode_table)))
    output.write(";\n")

    melissa_parser = MelissaZipParser()
    with open(source, 'r', encoding='utf8') as f:
        lines = f.readlines()

        sql_line = (
            "INSERT INTO {zipcode_table_path} "
            "(zip_code, state_name, city_name, county_name, latitude, "
            "longitude, msa, pmsa, geometry_point) VALUES ({values});\n"
        )
        # Lat and long are numbers so we don't have to quote them
        number_fields = (4, 5)
        for row in melissa_parser.process(lines):
            new_row = []
            for ix, value in enumerate(row):
                if value is None:
                    new_row.append('null')
                elif ix in number_fields:
                    new_row.append(str(value))
                else:
                    new_row.append(f"'{value}'")
            # geometry point using Longitude/Latitude from PostGIS
            latitude = row[4]
            longitude = row[5]
            new_row.append(f"ST_MakePoint({longitude}, {latitude})")
            output.write(
                sql_line.format(
                    zipcode_table_path=zipcode_table_path,
                    values=','.join(new_row)
                )
            )


def create_copy_statements(source, output):
    # Dismiss for now, we are going to use inserts instead
    melissa_parser = MelissaZipParser()
    with open(source, 'r', encoding='utf8') as f:
        lines = f.readlines()

        # Zipcode data
        output.write(
            "-- Dump zip code data\n"
            "COPY zip_code (zip_code, state_name, city_name, "
            "county_name, latitude, longitude, msa_name) FROM STDIN;\n"
        )
        # Add quotes to string fields on these indexes
        quoted_indexes = (0, 1, 2, 3, 4, 7)
        for row in melissa_parser.process(lines):
            new_row = ','.join(
                [
                    parse_type(x, str if i in quoted_indexes else int)
                    for i, x in enumerate(row)
                ]
            )
            output.write(f"({new_row})\n")


def parse_type(value, type_):
    if value is None:
        return ''
    if type_ in (int, float):
        return str(value)
    return f"'{value}'"


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('source', type=Path,
                    default=Path("zipdata/legacy/ZIP.DAT"),
                    help="Expected ZIP.DAT format")
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
