"""Step 1: load Synthea CSVs into Apache Iceberg tables in the `raw` namespace.

Replaces load_raw.py. DuckDB no longer stores the raw data: it reads these
Iceberg tables later (via iceberg_scan) when dbt runs.

    pip install "pyiceberg[sql-sqlite,pyarrow]"
    python load_raw_iceberg.py
"""
import shutil
from pathlib import Path

import pyarrow as pa
import pyarrow.csv as pv
from pyiceberg.catalog.sql import SqlCatalog

CSV_DIR = Path("/Users/camarenrogers/synthea/output/csv")
WAREHOUSE = (Path(__file__).parent / "warehouse").resolve()
WAREHOUSE.mkdir(exist_ok=True)

# The catalog is a small SQLite database that records, for every table name,
# which metadata file is the current one. The data itself lives in WAREHOUSE.
catalog = SqlCatalog(
    "local",
    uri=f"sqlite:///{WAREHOUSE}/catalog.db",
    warehouse=f"file://{WAREHOUSE}",
)
catalog.create_namespace_if_not_exists("raw")

for csv_file in sorted(CSV_DIR.glob("*.csv")):
    name = f"raw.{csv_file.stem}"
    data = pv.read_csv(csv_file)

    # Columns that are empty in every row (e.g. DEATHDATE when no one has died)
    # are inferred as type "null", which Iceberg can't store. Make them strings.
    data = data.cast(pa.schema(
        [pa.field(f.name, pa.string()) if pa.types.is_null(f.type) else f
         for f in data.schema]
    ))

    # Full reload for now, the same behaviour as the old CREATE OR REPLACE.
    # Step 2 swaps this for appends and upserts so history is kept.
    if catalog.table_exists(name):
        catalog.drop_table(name)
    # drop_table only removes the catalog's pointer; the old files stay on
    # disk. Delete them so each run starts from a clean folder.
    shutil.rmtree(WAREHOUSE / "raw" / csv_file.stem, ignore_errors=True)
    table = catalog.create_table(name, schema=data.schema)
    table.append(data)

    print(f"Loaded {name:20} {len(data):>7} rows")

print("\nDone. Iceberg warehouse at", WAREHOUSE)
