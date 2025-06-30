#!/bin/zsh

# Install Python dependencies
pip install -r requirements.txt

echo "Python dependencies installed."
# Navigate to the data folder
cd data

# Run schema.sql into the DuckDB database
duckdb demo_database.duckdb < schema.sql

echo "Setup complete. The DuckDB database has been initialized with the schema."