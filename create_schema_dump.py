from pathlib import Path
from sqlalchemy.schema import CreateTable
from leads_api.models.tables import metadata

base_path = Path('./docker-entrypoint-initdb.d/')

configs = [
    {
        'dbname': 'leads_db',
        'filename': 'schema.sql',
        'create_db': False,
    },
    {
        'dbname': 'leads_db_test',
        'filename': 'schema-test.sql',
        'create_db': True,
    },
]

def comment(f, text):
    f.write(f'\n-- {text}\n')

for config in configs:
    with open(base_path / config['filename'], 'w') as f:

        if config['create_db']:
            comment(f, f"Create database {config['dbname']}")
            f.write(f"DROP DATABASE IF EXISTS {config['dbname']};\n")
            f.write(f"CREATE DATABASE {config['dbname']};\n")

        comment(f, f"Connect to the database")
        f.write(f"\c {config['dbname']};\n")

        comment(f, "Tables definitions")
        for table in metadata.sorted_tables:
            comment(f, f"Create table `{table.name}`")
            create_table = CreateTable(table)
            f.write(str(create_table).strip() + ';\n')
