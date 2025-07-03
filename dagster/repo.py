from dagster import Definitions, EnvVar, load_assets_from_modules

import assets.adress_assets as adress_assets
import assets.person_assets as person_assets
from jobs.jobs import (
    populate_data_job,
    simulate_data_job,
)
from jobs.schedules import (
    populate_data_schedule,
    simulate_data_schedule,
)
from resources.drivers import DuckDBResource, Neo4jDriver


## A S S E T S ##
demo_asset_group = load_assets_from_modules(
    [adress_assets],  
    group_name="demo_assets"
)

person_assets_group = load_assets_from_modules(
    [person_assets],
    group_name="person_assets"
)
all_assets = demo_asset_group  + person_assets_group

## J O B S ##
all_jobs = [
    simulate_data_job,
    populate_data_job,
]

## S C H E D U L E S ##
all_schedules = [
    simulate_data_schedule,
    populate_data_schedule,
]

defs = Definitions(
    assets = all_assets,
    jobs=all_jobs,
    schedules=all_schedules,
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