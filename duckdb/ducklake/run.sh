#!/usr/bin/env bash
set -euo pipefail

# 1) Bring up Postgres + pgAdmin (with named volume "pgdata" as defined in your docker-compose.yml)
podman-compose up -d

echo "Waiting for Postgres to become ready (10s)…"
sleep 10

# 2) Use DuckDB CLI to:
#    • INSTALL + LOAD postgres + ducklake extensions
#    • ATTACH a DuckLake catalog backed by Postgres (metadata in pgdata volume,
#      data files in ./data_files)
#    • Create a 4-column table "sim_data", insert 20 rows, update two rows
#    • Show the table contents and list DuckLake snapshots
duckdb <<'SQL'
-- -------------------------------------------------------------------
-- 2a) (Only needed once) Ensure the extensions are installed:
INSTALL postgres;
INSTALL ducklake;

-- 2b) Load the extensions for this session:
LOAD postgres;
LOAD ducklake;

-- 2c) ATTACH a Postgres-backed DuckLake catalog.
--     Use a space-separated libpq connection string (no semicolons).
--     Postgres is on localhost:6543, dbname=postgres, user=duckuser, pass=duckpass.
--     All metadata tables (ducklake_snapshots, etc.) will live in Postgres’s "postgres" DB
--     (inside the named volume pgdata). Parquet files will go under ./data_files/.
ATTACH 'ducklake:postgres:host=localhost port=6543 dbname=postgres user=duckuser password=duckpass'
  AS my_ducklake(DATA_PATH 'data_files');

-- 2d) Switch into that DuckLake catalog
USE my_ducklake;

-- 2e) Create a 4-column table "sim_data"
CREATE TABLE sim_data (
    id       INTEGER,
    category VARCHAR,
    amount   INTEGER,
    flag     VARCHAR
);

-- Insert 20 rows of dummy data
INSERT INTO sim_data
SELECT
    i AS id,
    CASE WHEN i % 2 = 0 THEN 'even' ELSE 'odd' END   AS category,
    i * 10                                           AS amount,
    CASE WHEN i <= 10 THEN 'A' ELSE 'B' END          AS flag
FROM range(1, 21) AS t(i);

-- Update two specific rows:
UPDATE sim_data
SET category = 'updated_even'
WHERE id = 4;

UPDATE sim_data
SET amount = 999
WHERE id = 17;

-- 2f) Show the current contents of sim_data
SELECT *
FROM sim_data
ORDER BY id;

-- 2g) List all DuckLake snapshots (stored in Postgres under pgdata)
SELECT *
FROM my_ducklake.snapshots();
SQL

echo
echo "✅ Success! DuckLake catalog is live; sim_data created & updated."
echo
echo "  • Visit pgAdmin at http://localhost:8080  (login: admin@localhost / adminpass)"
echo "  • DuckLake metadata (snapshots, etc.) lives in the named volume 'pgdata'."
echo "  • Parquet data files for sim_data live under ./data_files/."

