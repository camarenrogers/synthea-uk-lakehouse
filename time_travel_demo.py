"""Lesson: append a second Synthea batch a second Synthea batch, then look at the table's history."""
from pathlib import Path

import duckdb
import pyarrow as pa
from pyiceberg.catalog.sql import SqlCatalog

WAREHOUSE = (Path(__file__).parent / "warehouse").resolve()
catalog = SqlCatalog("local", uri=f"sqlite:///{WAREHOUSE}/catalog.db",
                     warehouse=f"file://{WAREHOUSE}")
conditions = catalog.load_table("raw.conditions")

# A "second run" of Synthea: one new diagnosis for patient p2.
batch_2 = pa.Table.from_pylist(
    [{"START": None, "STOP": None, "PATIENT": "p2", "ENCOUNTER": "e2",
      "CODE": 125605004, "DESCRIPTION": "Fracture of bone"}],
    schema=conditions.schema().as_arrow(),
)
conditions.append(batch_2)   # <- this creates a new snapshot

print("History of raw.conditions:")
for snap in conditions.snapshots():
    rows = len(conditions.scan(snapshot_id=snap.snapshot_id).to_arrow())
    print(f"  snapshot {snap.snapshot_id}  {snap.summary.operation.value:6}  -> {rows} rows")

first = conditions.snapshots()[0].snapshot_id
con = duckdb.connect()
con.execute("LOAD iceberg; SET unsafe_enable_version_guessing = true;")
path = f"{WAREHOUSE}/raw/conditions"
print("\nNow:")
print(con.sql(f"select DESCRIPTION, count(*) n from iceberg_scan('{path}') group by 1"))
print("Before the second load (time travel):")
print(con.sql(f"select DESCRIPTION, count(*) n from iceberg_scan('{path}', snapshot_from_id={first}) group by 1"))
