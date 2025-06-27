from dagster import asset, AssetExecutionContext, MaterializeResult, MetadataValue, AssetIn
from resources.utils import Logg
from resources.drivers import DuckDBResource
import pandas as pd
import numpy as np

@asset( kinds={"duckdb"})
def simulate_data(context: AssetExecutionContext,
                  duckdb: DuckDBResource) -> MaterializeResult:
    """
    Simulates data for testing purposes.
    This asset generates a DataFrame with 100 rows and 3 columns.
    """

    df = pd.DataFrame({
        "id": np.arange(100),
        "value": np.random.rand(100),
        "category": np.random.choice(['A', 'B', 'C'], size=100)
    })
    
    # Write data to duckdb
    with duckdb.get_connection() as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS test_data AS SELECT * FROM df")
            Logg.info(context, "Data written to DuckDB table 'test_data'.")
            conn.close()

    return MaterializeResult(
        metadata={
            "num_rows": MetadataValue.int(len(df)),
            "num_columns": MetadataValue.int(len(df.columns)),
            "columns": MetadataValue.json({"columns": list(df.columns)}),
            "sample_data":  MetadataValue.md(df.head().to_markdown())
        }
    )