# synthea-uk-lakehouse

A small healthcare lakehouse built on synthetic UK patient records.
Raw data is stored as **Apache Iceberg** tables, queried by **DuckDB**,
and transformed into tested, analysis-ready tables with **dbt**.

This is v2 of [synthea-uk-pipeline](https://github.com/camarenrogers/synthea-uk-pipeline),
which kept everything inside a single DuckDB file.

## Architecture

```
Synthea (UK config) → CSV → PyIceberg → Iceberg tables (raw)
                                              ↓
                          DuckDB reads them with iceberg_scan
                                              ↓
                          dbt: staging views → marts tables
```

**Why Iceberg?** In v1, DuckDB both stored and queried the raw data.
Here those jobs are separate: the raw data lives in an open table format
(Parquet files plus Iceberg metadata) that any engine can read: DuckDB,
Spark, Trino, Snowflake. DuckDB is just the compute layer. Iceberg also
gives every load a **snapshot**, so past versions of a table can be
queried again (time travel).

## Project layout

| Path | What it is |
|---|---|
| `load_raw_iceberg.py` | Loads every Synthea CSV into an Iceberg table in the `raw` namespace |
| `warehouse/` | Iceberg data and metadata, plus the SQLite catalog (`catalog.db`). Not committed |
| `synthea_dbt/` | dbt project: `staging` models (cleaned, renamed) and `marts` |
| `time_travel_demo.py` | Appends a batch to a table and queries it before and after |

## Data models

**Staging** (one view per source): `stg_patients`, `stg_encounters`,
`stg_conditions`, `stg_observations`, `stg_medications`

**Marts:**
- `patient_summary`: one row per patient with demographics, age and encounter statistics
- `condition_prevalence`: conditions ranked by number of distinct patients

**Tests:** uniqueness and not-null checks on IDs, and referential integrity
between encounters and patients.

## How to run

1. Generate data with [Synthea International](https://github.com/synthetichealth/synthea-international)
   using the GB config, exporting CSV. Set `CSV_DIR` in `load_raw_iceberg.py` to that output folder.
2. Install dependencies:
   ```
   pip install "pyiceberg[sql-sqlite,pyarrow]" dbt-duckdb
   ```
3. Load the raw layer into Iceberg:
   ```
   python load_raw_iceberg.py
   ```
4. Add a `synthea_dbt` profile to `~/.dbt/profiles.yml`:
   ```yaml
   synthea_dbt:
     target: dev
     outputs:
       dev:
         type: duckdb
         path: <repo>/analytics.duckdb
         schema: main
         threads: 4
         extensions: [iceberg]
         settings:
           unsafe_enable_version_guessing: true
   ```
5. Build and test:
   ```
   cd synthea_dbt
   dbt build
   ```

## Design notes

- **Local catalog.** Tables are registered in a SQLite catalog through PyIceberg.
  DuckDB can't read that catalog, so it finds each table's current version by
  taking the highest-numbered metadata file (`unsafe_enable_version_guessing`).
  That's fine locally; the planned REST catalog removes the need for it.
- **Empty columns.** Synthea columns that are empty in every row (for example
  `DEATHDATE`) are read as a null type, which Iceberg can't store. The loader
  stores them as strings.
- **Full reloads.** Each run currently drops and recreates the raw tables.
  Incremental loading is the next step.

## Roadmap

- [x] **Step 1:** raw layer in Iceberg (PyIceberg + SQLite catalog), dbt reads via `iceberg_scan`
- [ ] **Step 2:** incremental loads (one snapshot per Synthea run) and patient upserts
- [ ] **Step 3:** time-travel notebook comparing marts before and after a load
- [ ] **Step 4:** schema evolution and monthly partitioning of encounters and observations
- [ ] **Step 5:** Docker Compose with MinIO and an Iceberg REST catalog, plus CI

## Tech stack

Synthea · Python · PyIceberg · Apache Iceberg · DuckDB · dbt · SQL
