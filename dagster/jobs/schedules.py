from dagster import ScheduleDefinition
from jobs.jobs import populate_data_job, simulate_data_job

# Define schedules for the jobs
simulate_data_schedule = ScheduleDefinition(
    job=simulate_data_job,
    cron_schedule="0 0 * * *",  # Runs daily at midnight
    execution_timezone="Europe/Oslo",
    description="Daily job to simulate data for testing purposes."
)
populate_data_schedule = ScheduleDefinition(
    job=populate_data_job,
    cron_schedule="0 1 * * *",  # Runs daily at 1 AM
    execution_timezone="Europe/Oslo",
    description="Daily job to populate data into the silver layer."
)