from dagster import load_assets_from_modules, Definitions, define_asset_job, AssetSelection, EnvVar, ScheduleDefinition
import assets.demo_assets as demo_assets
from resources.drivers import Neo4jDriver, DuckDBResource

demo_asset_group = load_assets_from_modules(
    [demo_assets],  
    group_name="demo_assets"
)

all_assets = demo_asset_group  
defs = Definitions(
    assets = all_assets,
    #jobs=[delta_job_bisnode, organisationer_delta_job],
    #schedules=[organisationer_delta_schedule],
    resources={
        "neo4j": Neo4jDriver(
            uri="bolt://localhost:7687",
            user= EnvVar("NEO4J_USER"),
            password=EnvVar("NEO4J_PWD")

        ),
        "duckdb": DuckDBResource(
            database="data/demo_database.duckdb",  
        )
    }
)