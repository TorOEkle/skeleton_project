from dagster import asset, AssetExecutionContext, MaterializeResult, MetadataValue

from functions.simulate_data import generate_norwegian_addresses
from functions.transformations import transform_adress
from resources.drivers import DuckDBResource
from resources.utils import adress_partitions, Logg, measure_time_with_metadata


CHUNK_SIZE = 50000  

@asset( kinds={"duckdb", "bronze"})
@measure_time_with_metadata
def simulate_adress_data(context: AssetExecutionContext,
                  duckdb: DuckDBResource) -> MaterializeResult:
    """
    Simulates data for testing purposes.
    This asset simulate adress data and stores it in a DuckDB table named 'adress_bronze'.
    """

    adress = generate_norwegian_addresses(n_addresses=1000)
    Logg.info(context, f"Generated {len(adress)} addresses.")
    
    # Write data to duckdb
    with duckdb.get_connection() as conn:
            conn.execute("""
                     CREATE OR REPLACE TABLE adress_bronze AS 
                     SELECT 
                         household_id,
                         street_address,
                         zip_code,
                         location
                     FROM adress
                         """)
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

@asset(
          deps = [simulate_adress_data], partitions_def=adress_partitions, 
          kinds={"duckdb", "silver"})
@measure_time_with_metadata
def adress_silver(context: AssetExecutionContext,duckdb: DuckDBResource,) -> MaterializeResult:
    """
    This asset transforms the adress data from the 'adress_bronze' table
    and stores it in a new table named 'adress_silver'.
    """
    start_id = int(context.partition_key)
    end_id = start_id + CHUNK_SIZE  
    Logg.info(context, f"Transforming adress data for partition: {start_id}")
    with duckdb.get_connection() as conn:
        # Read data from the 'adress_bronze' table
        adress = conn.execute(f"""
                              SELECT * FROM adress_bronze WHERE household_id > {start_id} AND household_id <= {end_id}
                              """).fetchdf()
        Logg.info(context, f"Read {len(adress)} rows from 'adress_bronze'.")
        adress = transform_adress(adress)       
        # Write transformed data to the 'adress_silver' table
        conn.execute("""
                    INSERT INTO adress_silver (household_id, street_address, zip_code, location, full_adress) 
                    SELECT household_id, street_address, zip_code, location, full_adress 
                    FROM adress
                     """)
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