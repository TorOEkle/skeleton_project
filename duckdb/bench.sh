# ┌─────────────────────────────────────────────────────
# │ bench.sh: DuckDB single-threaded join benchmark
# └─────────────────────────────────────────────────────
#!/usr/bin/env bash
set -euo pipefail

DB_FILE="join_benchmark.db"
SQL_FILE="benchmark.sql"

rm -f "${DB_FILE}"

cat > "${SQL_FILE}" <<'EOF'
-- force single-threaded
PRAGMA threads=1;
PRAGMA memory_limit='4GB';

-- create t1: 10M sequential
CREATE TABLE t1 AS
  SELECT id, random() AS value1
  FROM range(10000000) AS t(id);

-- create t2: 2M random IDs in [0..9_999_999]
CREATE TABLE t2 AS
  SELECT (abs(random()) % 10000000)::INTEGER AS id,
         random() AS value2
  FROM range(2000000);

-- warm up
SELECT COUNT(*) FROM t1;
SELECT COUNT(*) FROM t2;

-- measure join
EXPLAIN ANALYZE
SELECT COUNT(*) AS match_count
FROM t1
JOIN t2 USING(id);
EOF

echo "=== DuckDB (1 thread) ==="
duckdb "${DB_FILE}" < "${SQL_FILE}" | awk '/Total Time/'

