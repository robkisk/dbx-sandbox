"""Main application module for Databricks data processing.

This module provides functionality to query and process data from Databricks tables.
It supports both local execution via Databricks Connect and remote execution on
Databricks clusters, automatically detecting and using the appropriate Spark session.

Example:
    Run locally with Databricks Connect::

        $ uv run python -m databricks_connect.main

    Deploy and run on Databricks cluster::

        $ databricks bundle deploy -t dev
        $ databricks bundle run main_task -t dev
"""

from pyspark.sql import DataFrame, SparkSession


def get_spark() -> SparkSession:
  """Get or create a Spark session appropriate for the execution environment.

  This function attempts to use the Databricks Runtime spark session when running
  on a Databricks cluster. If not available (e.g., when running locally), it falls
  back to creating a Databricks Connect session with serverless compute.

  Returns:
      SparkSession: An active Spark session configured for the current environment.

  Raises:
      Exception: If Databricks Connect configuration is invalid or credentials
          are not properly configured.

  Example:
      >>> spark = get_spark()
      >>> df = spark.read.table('samples.nyctaxi.trips')
      >>> df.count()
      200000
  """
  try:
    # Try to get Databricks Runtime spark (only works on cluster)
    from databricks.sdk.runtime import spark

    if spark is not None:
      return spark
  except (ImportError, RuntimeError):
    pass

  # Fall back to Databricks Connect for local development
  from databricks.connect import DatabricksSession

  return DatabricksSession.builder.profile('dev').serverless().getOrCreate()


def find_all_taxis() -> DataFrame:
  """Retrieve all records from the NYC taxi trips sample dataset.

  Queries the Databricks samples dataset to fetch NYC taxi trip data. This
  function demonstrates basic table reading functionality and serves as an
  example for data processing pipelines.

  Returns:
      DataFrame: A PySpark DataFrame containing NYC taxi trip records with
          columns including pickup/dropoff timestamps, trip distance, fare
          amount, and zip codes.

  Raises:
      Exception: If the table does not exist or if there are permission issues
          accessing the samples catalog.

  Example:
      >>> df = find_all_taxis()
      >>> df.select('trip_distance', 'fare_amount').show(5)
      +-------------+-----------+
      |trip_distance|fare_amount|
      +-------------+-----------+
      |          1.4|        8.0|
      +-------------+-----------+
  """
  spark = get_spark()
  return spark.read.table('samples.nyctaxi.trips')


def main() -> None:
  """Main entry point for the application.

  Executes the primary data processing workflow by retrieving taxi trip data
  and displaying a sample of the results. This function is called when the
  module is executed directly or via the Python wheel task entry point.

  Example:
      >>> main()
      +--------------------+---------------------+-------------+-----------+
      |tpep_pickup_datetime|tpep_dropoff_datetime|trip_distance|fare_amount|
      +--------------------+---------------------+-------------+-----------+
      | 2016-02-13 21:47:53|  2016-02-13 21:57:15|          1.4|        8.0|
      +--------------------+---------------------+-------------+-----------+
  """
  find_all_taxis().show(5)


if __name__ == '__main__':
  main()
