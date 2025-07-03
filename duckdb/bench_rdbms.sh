#!/usr/bin/env bash
set -euo pipefail

# 1) Start Postgres & MySQL
podman-compose up -d

# 2) Wait for Postgres
echo "Waiting for Postgres..."
until podman-compose exec -T postgres pg_isready -U postgres >/dev/null 2>&1; do sleep 1; done

# 3) Wait for MySQL
echo "Waiting for MySQL (login test)…"
until podman-compose exec -T mysql mysql -uroot -ppassword -e "SELECT 1" >/dev/null 2>&1; do sleep 1; done

# 4) Load data into Postgres
echo "Loading data into Postgres…"
podman-compose exec -T postgres psql -U postgres -d benchdb <<'EOF'
-- single-threaded
SET max_parallel_workers_per_gather = 0;
SET max_parallel_workers        = 0;

DROP TABLE IF EXISTS t1, t2;

-- t1: 10M sequential IDs
CREATE TABLE t1 AS
  SELECT i AS id, random() AS value1
  FROM generate_series(0,9999999) AS gs(i);

-- t2: 2M random IDs in [0..9_999_999]
CREATE TABLE t2 AS
  SELECT (trunc(random()*10000000))::int AS id,
         random() AS value2
  FROM generate_series(1,2000000) AS gs(i);

-- index them
CREATE INDEX ON t1(id);
CREATE INDEX ON t2(id);
EOF

# 5) Load data into MySQL
echo "Loading data into MySQL…"
podman-compose exec -T mysql mysql -uroot -ppassword benchdb <<'EOF'
DROP TABLE IF EXISTS t1, t2;

CREATE TABLE t1 (
  id     INT PRIMARY KEY,
  value1 DOUBLE
);

-- 10M sequential
SET @row = -1;
INSERT INTO t1 (id, value1)
SELECT (@row := @row + 1), RAND()
FROM (SELECT 1 UNION ALL SELECT 1) a,
     (SELECT 1 UNION ALL SELECT 1) b,
     (SELECT 1 UNION ALL SELECT 1) c,
     (SELECT 1 UNION ALL SELECT 1) d
LIMIT 10000000;

CREATE TABLE t2 (
  id     INT,
  value2 DOUBLE,
  INDEX idx_id (id)
);

-- 2M *truly* random* IDs via CRC32(UUID())
INSERT INTO t2 (id, value2)
SELECT CAST(CRC32(UUID()) % 10000000 AS UNSIGNED), RAND()
FROM (SELECT 1 UNION ALL SELECT 1) a,
     (SELECT 1 UNION ALL SELECT 1) b,
     (SELECT 1 UNION ALL SELECT 1) c,
     (SELECT 1 UNION ALL SELECT 1) d,
     (SELECT 1 UNION ALL SELECT 1) e
LIMIT 2000000;

/* Verify distribution */
SELECT 't2 MIN,MAX' AS note, MIN(id), MAX(id) FROM t2;
SELECT 't2 COUNT'      AS note, COUNT(*)    FROM t2;
EOF

# 6) DuckDB (single-thread)
echo
echo "=== DuckDB (1 thread) ==="
./bench.sh

# 7) Postgres timing
echo
echo "=== Postgres (single-thread) ==="
podman-compose exec -T postgres psql -U postgres -d benchdb <<'EOF'
\timing on
EXPLAIN ANALYZE
SELECT COUNT(*) AS match_count
FROM t1
JOIN t2 USING(id);
EOF

# 8) MySQL timing
echo
echo "=== MySQL (single-thread) ==="
podman-compose exec -T mysql mysql -uroot -ppassword benchdb <<'EOF'
SELECT COUNT(*) AS match_count
FROM t1
JOIN t2 USING(id);
EOF

# 9) Tear down
podman-compose down

