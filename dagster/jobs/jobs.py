from dagster import AssetSelection, define_asset_job

import assets.adress_assets as adress_assets
import assets.person_assets as person_assets


## Define jobs

simulate_data_job = define_asset_job(
    "simulate_data_job",
    selection=AssetSelection.assets(
        adress_assets.simulate_adress_data,
        person_assets.simulate_person_data_asset
    ),
    description="Simulates data for testing purposes."
)

populate_data_job = define_asset_job(
    "populate_data_job",
    selection=AssetSelection.assets(
        adress_assets.adress_silver,
        person_assets.create_household_income
    ),
    description="Populates data into the silver layer."
)
