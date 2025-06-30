from dagster import asset, AssetExecutionContext, MaterializeResult, MetadataValue, AssetIn
import pandas as pd
from resources.utils import Logg, measure_time_with_metadata
from resources.drivers import DuckDBResource
from functions.simulate_data import simulate_person_data
import matplotlib.pyplot as plt