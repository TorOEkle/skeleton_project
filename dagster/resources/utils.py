from dagster import (
    DailyPartitionsDefinition,
    DynamicPartitionsDefinition,
    MonthlyPartitionsDefinition,
    StaticPartitionsDefinition,
)

TOTAL_ROWS = 4100000
CHUNK_SIZE = 100000  # Define chunk size

partition_values = [str(i) for i in range(0, TOTAL_ROWS, CHUNK_SIZE)]
# Define numeric partitions
partitions = StaticPartitionsDefinition(partition_values)


# Månadlig partitionering
# Den starter den 1. månaden efter start_date, end_offset = 1 ==> upp til dagens datum.
monthly_partition = MonthlyPartitionsDefinition(start_date="2014-12-24", end_offset=1)

# Partitionering för Excel-filer (Avtal och uppföljning)
filename_partition = DynamicPartitionsDefinition(name="filenames")

class Logg:
    """
    Logg is a helper class designed to log messages within a given context.
    It contains static methods that can be used to log informational and error messages.
    
    Static methods:
        info(context, msg: str) -> None:
            Logs an informational message using the context's logging mechanism,
            if a context is available.
        error(context, msg: str) -> None:
            Logs an error message using the context's logging mechanism,
            if a context is available.
    """

    @staticmethod
    def info(context, msg):
        if context:
            context.log.info(msg)

    @staticmethod
    def error(context, msg):
        if context:
            context.log.error(msg)

    @staticmethod
    def debug(context, msg):
        if context:
            context.log.debug(msg)

    @staticmethod
    def warning(context, msg):
        if context:
            context.log.warning(msg)

    @staticmethod
    def critical(context, msg):
        if context:
            context.log.critical(msg)