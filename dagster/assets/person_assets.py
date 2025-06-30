import base64
import io

from dagster import asset, AssetExecutionContext, MaterializeResult, MetadataValue
import matplotlib.pyplot as plt

from functions.simulate_data import simulate_person_data
from resources.drivers import DuckDBResource
from resources.utils import Logg, measure_time_with_metadata


@asset(
        kinds={"duckdb", "bronze", "matplotlib"}, 
        deps =['simulate_adress_data'])
@measure_time_with_metadata
def simulate_person_data_asset(context: AssetExecutionContext, duckdb: DuckDBResource) -> MaterializeResult:
    """
    Simulates person data for testing purposes.
    This asset simulates person data and stores it in a DuckDB table named 'person_bronze'.
    """
    # Read household_id values from adress_bronze table
    with duckdb.get_connection() as conn:
        household_ids = conn.execute("SELECT household_id FROM adress_bronze").fetchdf()['household_id']
        Logg.info(context, f"Retrieved {len(household_ids)} household IDs from adress_bronze.")
        
        # Generate person data using the household IDs
        person_data = simulate_person_data(household_ids)
        Logg.info(context, f"Generated {len(person_data)} person records.")

        # Write data to DuckDB
        conn.execute("""    
                            INSERT INTO persons_bronze (person_id, household_id, name, year_of_birth, income) 
                            SELECT person_id, household_id, name, year_of_birth, income 
                            FROM person_data
                     """)
        Logg.info(context, "Data written to DuckDB table 'persons_bronze'.")
        conn.close()

         # Create matplotlib plot
        plt.figure(figsize=(10, 6))
        plt.scatter(person_data['year_of_birth'], person_data['income'], alpha=0.6)
        plt.xlabel('Year of Birth')
        plt.ylabel('Income')
        plt.title('Income vs Year of Birth')
        plt.grid(True, alpha=0.3)

        # Convert plot to base64 string for inline display
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        plot_data = base64.b64encode(buffer.getvalue()).decode()
        plt.close()

    return MaterializeResult(
        metadata={
            "num_rows": MetadataValue.int(len(person_data)),
            "num_columns": MetadataValue.int(len(person_data.columns)),
            "columns": MetadataValue.json({"columns": list(person_data.columns)}),
            "sample_data": MetadataValue.md(person_data.head().to_markdown()),
            "income_vs_yob_plot": MetadataValue.md(f"![Income vs Year of Birth](data:image/png;base64,{plot_data})")
        }
    )

@asset(
        deps=[simulate_person_data_asset,"adress_silver"], 
        kinds={"duckdb", "gold", "matplotlib"})
@measure_time_with_metadata
def create_household_income(context: AssetExecutionContext, duckdb: DuckDBResource) -> MaterializeResult:
    """
    This asset creates a household income table from the person data.
    It calculates the mean year of birth and total household income for each household.
    """
    with duckdb.get_connection() as conn:
        # Write household data to DuckDB
        conn.execute("""
                    INSERT INTO household_gold (household_id, mean_yob, household_income, full_adress)
                    SELECT 
                        p.household_id,
                        AVG(p.year_of_birth) AS mean_yob,
                        SUM(p.income) AS household_income,
                        a.full_adress
                    FROM persons_bronze p
                    LEFT JOIN adress_silver a ON p.household_id = a.household_id
                    GROUP BY p.household_id, a.full_adress;
                     """)
        Logg.info(context, "Data written to DuckDB table 'household_gold'. Read back to create plot.")
        # Read person data from the 'person_bronze' table
        household_data = conn.execute("SELECT mean_yob, household_income  FROM household_gold").fetchdf()
        Logg.info(context, "Create plot for household income vs mean year of birth.")
        conn.close()
        # Create matplotlib plot
        plt.figure(figsize=(10, 6))
        plt.scatter(household_data['mean_yob'], household_data['household_income'], alpha=0.6)
        plt.xlabel('Mean Year of Birth')
        plt.ylabel('Household Income')
        plt.title('Household Income vs Mean Year of Birth')
        plt.grid(True, alpha=0.3)

        # Convert plot to base64 string for inline display
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        plot_data = base64.b64encode(buffer.getvalue()).decode()
        plt.close()

    return MaterializeResult(
        metadata={
            "num_rows": MetadataValue.int(len(household_data)),
            "num_columns": MetadataValue.int(len(household_data.columns)),
            "columns": MetadataValue.json({"columns": list(household_data.columns)}),
            "sample_data": MetadataValue.md(household_data.head().to_markdown()),
            "household_income_vs_mean_yob_plot": MetadataValue.md(f"![Household Income vs Mean YoB](data:image/png;base64,{plot_data})")
        }
    )