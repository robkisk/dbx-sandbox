# COMMAND ----------
"""Databricks Connect demonstration script.

This module demonstrates basic Databricks Connect functionality including
session creation, configuration retrieval, and table operations.
"""

from typing import Optional
from databricks.connect import DatabricksSession
from pyspark.sql import SparkSession


def create_databricks_session(profile: str = 'dev') -> SparkSession:
  """Create and return a Databricks session.

  Args:
      profile: The Databricks profile to use for connection.

  Returns:
      A configured Spark session connected to Databricks.

  Raises:
      Exception: If session creation fails.
  """
  try:
    session = DatabricksSession.builder.profile(profile).serverless().getOrCreate()
    return session
  except Exception as e:
    raise Exception(f'Failed to create Databricks session: {e}')


def get_workspace_info(spark: SparkSession) -> tuple[Optional[str], Optional[str]]:
  """Retrieve workspace configuration information.

  Args:
      spark: The Spark session to query.

  Returns:
      A tuple containing (workspace_url, cluster_id).
  """
  try:
    workspace_url = spark.conf.get('spark.databricks.workspaceUrl')
    cluster_id = spark.conf.get('spark.databricks.clusterUsageTags.clusterId')
    return workspace_url, cluster_id
  except Exception as e:
    print(f'Error retrieving workspace info: {e}')
    return None, None


def display_sample_data(
  spark: SparkSession, table_name: str = 'samples.nyctaxi.trips', num_rows: int = 10
) -> None:
  """Display sample data from a Databricks table.

  Args:
      spark: The Spark session to use.
      table_name: Name of the table to query.
      num_rows: Number of rows to display.
  """
  try:
    spark.table(table_name).show(num_rows, False)
  except Exception as e:
    print(f'Error displaying sample data from {table_name}: {e}')


def main() -> None:
  """Main function demonstrating Databricks Connect functionality."""
  spark = create_databricks_session()

  workspace_url, cluster_id = get_workspace_info(spark)

  print(f'Workspace URL: {workspace_url}')
  print(f'Cluster ID: {cluster_id}')

  display_sample_data(spark)


if __name__ == '__main__':
  main()

# COMMAND ----------
