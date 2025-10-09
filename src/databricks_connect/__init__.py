"""Databricks App Template.

Modern Databricks application template with FastAPI backend and React TypeScript frontend.
"""

__version__ = '0.1.0'

# Expose main components for easier imports
from databricks_connect.dbcn import (
  create_databricks_session,
  get_workspace_info,
  display_sample_data,
)

# Expose main entry point for the job
from databricks_connect.main import main

__all__ = [
  'create_databricks_session',
  'get_workspace_info',
  'display_sample_data',
  'main',
]
