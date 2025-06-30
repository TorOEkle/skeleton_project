from dagster import asset, AssetExecutionContext, MaterializeResult, MetadataValue, AssetIn
from resources.utils import Logg, measure_time_with_metadata, adress_partitions
from resources.drivers import DuckDBResource
import pandas as pd
import matplotlib.pyplot as plt
from functions.simulate_data import generate_norwegian_addresses


@asset( kinds={"duckdb", "bronze"})
@measure_time_with_metadata
def simulate_adress_data(context: AssetExecutionContext,
                  duckdb: DuckDBResource) -> MaterializeResult:
    """
    Simulates data for testing purposes.
    This asset simulate adress data and stores it in a DuckDB table named 'adress_bronze'.
    """

    adress = generate_norwegian_addresses(n_addresses=100)
    Logg.info(context, f"Generated {len(adress)} addresses.")
    
    # Write data to duckdb
    with duckdb.get_connection() as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS adress_bronze AS SELECT * FROM adress")
            Logg.info(context, "Data written to DuckDB table 'adress_bronze'.")
            conn.close()

    return MaterializeResult(
        metadata={
            "num_rows": MetadataValue.int(len(adress)),
            "num_columns": MetadataValue.int(len(adress.columns)),
            "columns": MetadataValue.json({"columns": list(adress.columns)}),
            "sample_data":  MetadataValue.md(adress.head().to_markdown())
        }
    )

@asset(deps = [simulate_adress_data], partitions_def=adress_partitions)
@measure_time_with_metadata
def transform_adress(context: AssetExecutionContext,duckdb: DuckDBResource,) -> MaterializeResult:
    """
    This asset transforms the adress data from the 'adress_bronze' table
    and stores it in a new table named 'adress_silver'.
    """
    partition_key = context.partition_key
    Logg.info(context, f"Transforming adress data for partition: {partition_key}")
    with duckdb.get_connection() as conn:
        # Read data from the 'adress_bronze' table
        adress = conn.execute(f"SELECT * FROM adress_bronze WHERE adress_id < {partition_key}").fetchdf()
        Logg.info(context, f"Read {len(adress)} rows from 'adress_bronze'.")
        # Transform the 'address' column
        adress[['street', 'city', 'zip_code']] = adress['street_address'].str.split(',', expand=True)
        
        Logg.info(context, "Transformed 'street_address' into 'street', 'city', and 'zip_code'.")
        # Write transformed data to the 'adress_silver' table
        conn.execute("CREATE TABLE IF NOT EXISTS adress_silver AS SELECT * FROM adress")
        Logg.info(context, "Data written to DuckDB table 'adress_silver'.") 
        conn.close()
    return MaterializeResult(
        metadata={
            "num_rows": MetadataValue.int(len(adress)),
            "num_columns": MetadataValue.int(len(adress.columns)),
            "columns": MetadataValue.json({"columns": list(adress.columns)}),
            "sample_data":  MetadataValue.md(adress.head().to_markdown())
        }
    )