# CLAUDE.md

## Repository Purpose
This folder is used for deploying Databricks Asset Bundles (DABs) and Terraform configurations to Databricks workspaces.

## Key Principles
- You are an AI assistant specialized in Python development. Your approach emphasizes:
- Clear project structure with separate directories for source code, tests, docs, and config.
- Detailed documentation using docstrings and README files.
- Dependency management via https://github.com/astral-sh/uv and virtual environments.
- Code style consistency using Ruff.
- Prefer functional programming over OOP
- Follow DRY, KISS, and YAGNI principles
- For any python file, be sure to ALWAYS add typing annotations to each function or class. Be sure to include return types when necessary. Add descriptive docstrings to all python functions and classes as well. Please use pep257 convention. Update existing docstrings if need be.
- Make sure you keep any comments that exist in a file.

## Python Package Management with uv
Use uv exclusively for Python package management in this project.

- All Python dependencies **must be installed, synchronized, and locked** using uv
- Never use pip, pip-tools, poetry, or conda directly for dependency management

### Install dependencies
- install project deps: `uv sync`
- install project deps with an extra: `uv sync --extra foo`
- Remove dependencies with `uv remove <package>`
- If you're going to install a new library, do this using `uv add` and use the utility canonically.

### Running scripts & Python Code
- run script with existing project deps: `uv run some/script.py`
- run script additional deps on the fly: `uv run --with pandas script.py`
- Run a Python script with `uv run <script-name>.py`
- Run Python tools like Pytest with `uv run pytest` or `uv run ruff`

### Testing
- test all: `uv run pytest`
- test all with 3 runners: `uv run pytest -n3`
- test certain folder, only matching cases: `uv run pytest tests/basic -k some_test_fn_subtr`

## 🚨 DATABRICKS CLI EXECUTION RULE 🚨
- My locally installed `databricks` cli command is aliased as `db` so anytime I mention an instruction with `db` it refers to `databricks` cli.
- When creating self-contained bash scripts, always just use the full name to the cli `databricks` instead of `db`

**NEVER run `databricks` CLI directly - ALWAYS prefix with environment setup:**

```bash
# ✅ CORRECT - Always source .env.local first
source .env.local && export DATABRICKS_HOST && export DATABRICKS_TOKEN && databricks current-user me
source .env.local && export DATABRICKS_HOST && export DATABRICKS_TOKEN && databricks apps list
source .env.local && export DATABRICKS_HOST && export DATABRICKS_TOKEN && databricks workspace list /

# ❌ WRONG - Never use databricks CLI directly
databricks current-user me
databricks apps list
databricks workspace list /
```

**Why this is required:**
- Ensures environment variables are loaded from .env.local
- Exports authentication variables to environment
- Prevents authentication failures and missing configuration

### Environment Configuration
- Use `.env.local` for local development configuration
- Set environment variables and Databricks credentials
- Never commit `.env.local` to version control

## Databricks Asset Bundles (DABs)

### Official Documentation & Examples
**IMPORTANT**: Always refer to the official Databricks documentation and examples for the most up-to-date syntax and usage:
- **Documentation**: https://docs.databricks.com/aws/en/dev-tools/bundles
- **Example Bundles**: https://github.com/databricks/bundle-examples/tree/main
- **Common patterns and best practices**: https://github.com/databricks/bundle-examples 
- **Authenticate access to Databricks using OAuth token federation:** https://docs.databricks.com/aws/en/dev-tools/auth/oauth-federation
- **Authentication for Databricks Asset Bundles:** https://docs.databricks.com/aws/en/dev-tools/bundles/authentication
- **Bundle configuration examples:** https://docs.databricks.com/aws/en/dev-tools/bundles/examples
- **Continuous integration and delivery on Azure Databricks using Azure DevOps:** https://learn.microsoft.com/en-us/azure/databricks/dev-tools/ci-cd/azure-devops
- **Databricks Asset Bundle configuration:** https://docs.databricks.com/aws/en/dev-tools/bundles/settings
- **Databricks Asset Bundle configuration:** https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/settings
- **Enable workload identity federation for Azure DevOps Pipelines:** https://docs.databricks.com/aws/en/dev-tools/auth/provider-azure-devops
- **Lifecycle of a bundle:** https://docs.databricks.com/aws/en/dev-tools/bundles/work-tasks#lifecycle
- **Substitutions and variables in Databricks Asset Bundles:** https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/variables
- **What are Databricks Asset Bundles?:** https://docs.databricks.com/aws/en/dev-tools/bundles/
- **What is the Databricks CLI?:** https://docs.databricks.com/aws/en/dev-tools/cli
- **bundle command group:** https://docs.databricks.com/aws/en/dev-tools/cli/bundle-commands#init
- **Databricks CICD Best Practices:** https://docs.databricks.com/aws/en/dev-tools/ci-cd/best-practices
- **Databricks Asset Bundle Schema Spec:** https://gist.github.com/robkisk/d8d4d60228f0f073b609df775bffcf02

- Always validate bundles before deployment using `databricks bundle validate`
- Use environment-specific configurations under `targets` section (dev/staging/prod)
- Keep sensitive values in environment variables, not in databricks.yml
- Use bundle variables for reusable configurations
- Use Python cells in notebooks for dynamic SQL with variables (SQL cells don't support variable interpolation)
- Follow the structure patterns from the official examples repository for consistency
- **Use serverless compute by default** - Do not specify `new_cluster` configuration in tasks unless explicitly required
    - Specify environment_key for task instead
    - If no environment is defined for the job, define "default" with spec.environment_version=3

### Project Structure
- DAB projects should follow the standard structure with `databricks.yml` at the root
- Resources are defined in the `resources/` directory
- Environments are configured under `targets` section in databricks.yml (not `environments`)

### Common Commands
```bash
# Initialize a new DAB project
databricks bundle init

# Validate bundle configuration
databricks bundle validate

# Deploy to a specific environment
databricks bundle deploy -t <environment>

# Run a job defined in the bundle
databricks bundle run <job-name> -t <environment>

# Destroy deployed resources
databricks bundle destroy -t <environment>
```

## Databricks Apps Development

### Overview
Databricks Apps are data and AI applications that run directly on Databricks, supporting frameworks like Streamlit, Dash, Flask, and Gradio. Apps can be developed locally and deployed via Asset Bundles.

### Official Resources
- **App Development**: https://docs.databricks.com/aws/en/dev-tools/databricks-apps/app-development
- **App Templates**: https://github.com/databricks/app-templates
- **Bundle Tutorial**: https://docs.databricks.com/aws/en/dev-tools/bundles/apps-tutorial
- **Streamlit Docs**: https://docs.streamlit.io/get-started/tutorials/create-an-app

### App Configuration Files

#### 1. `app.yaml` (Required)
Defines app startup command and configuration:
```yaml
entrypoint: streamlit run app.py --server.port 8501
# or for other frameworks:
# entrypoint: python app.py
# entrypoint: gradio app.py
```

#### 2. `requirements.txt` (Required)
Python package dependencies:
```txt
streamlit>=1.28.0
pandas
numpy
databricks-sdk
```

#### 3. `databricks.yml` (For Bundle Deployment)
```yaml
bundle:
  name: my_app_bundle

resources:
  apps:
    my_streamlit_app:
      name: "my-streamlit-app"
      source_code_path: ./app
      description: "Value Advisor Streamlit App"

targets:
  dev:
    mode: development
    workspace:
      root_path: /Workspace/Users/${workspace.current_user.userName}/apps
  
  prod:
    mode: production
    workspace:
      root_path: /Workspace/apps/production
```

### Streamlit on Databricks

#### Basic App Structure
```python
import streamlit as st
import pandas as pd
from databricks.sdk import WorkspaceClient

# Page config
st.set_page_config(page_title="Value Advisor", layout="wide")

# Title
st.title("Value Advisor Dashboard")

# Sidebar
with st.sidebar:
    st.header("Filters")
    selected_type = st.selectbox("Type", ["All", "Cost", "Performance"])

# Main content
col1, col2 = st.columns(2)
with col1:
    st.metric("Total Recommendations", 42)
with col2:
    st.metric("Potential Savings", "$12,500")

# Data display
df = pd.DataFrame({"ID": [1, 2], "Action": ["Optimize", "Scale"]})
st.dataframe(df)

# Charts
st.bar_chart(df)

# Interactive widgets
if st.button("Refresh"):
    st.rerun()
```

#### Key Streamlit Components
- **Display**: `st.write()`, `st.markdown()`, `st.title()`, `st.header()`
- **Data**: `st.dataframe()`, `st.table()`, `st.json()`
- **Charts**: `st.line_chart()`, `st.bar_chart()`, `st.map()`
- **Inputs**: `st.text_input()`, `st.selectbox()`, `st.slider()`, `st.checkbox()`
- **Layout**: `st.columns()`, `st.sidebar`, `st.container()`, `st.tabs()`
- **State**: `st.session_state` for maintaining state between reruns
- **Performance**: `@st.cache_data` decorator for caching expensive operations

### Development Workflow

#### 1. Local Development
```bash
# Create app directory
mkdir my-app && cd my-app

# Create required files
touch app.py app.yaml requirements.txt

# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run app.py

# Or with Databricks CLI
databricks apps run-local
```

#### 2. Bundle Development
```bash
# Initialize bundle with app
databricks bundle init

# Generate from existing app
databricks bundle generate app

# Validate bundle
databricks bundle validate

# Deploy to workspace
databricks bundle deploy -t dev

# Run the app
databricks bundle run my_streamlit_app -t dev
```

#### 3. Debugging
```bash
# Run with debug output
databricks apps run-local --debug

# Prepare environment without running
databricks apps run-local --prepare-environment
```

### Environment Variables
Databricks automatically provides:
- `DATABRICKS_HOST`: Workspace URL
- `DATABRICKS_TOKEN`: Authentication token
- `DATABRICKS_WAREHOUSE_ID`: SQL warehouse ID (if configured)
- Custom variables can be set in `app.yaml`

### Project Structure Example
```
my-value-advisor-app/
├── databricks.yml       # Bundle configuration
├── app/                 # App source code
│   ├── app.py          # Main Streamlit app
│   ├── app.yaml        # App configuration
│   ├── requirements.txt# Python dependencies
│   ├── pages/          # Multi-page app pages
│   │   ├── 1_Analytics.py
│   │   └── 2_Settings.py
│   └── utils/          # Helper modules
│       └── data.py
└── resources/          # Static resources
    └── logo.png
```

### Best Practices for Databricks Apps

#### Development
- Use virtual environments for local development
- Test locally with `databricks apps run-local` before deployment
- Keep `requirements.txt` minimal and specific
- Use environment variables for configuration

#### Streamlit Specific
- Use `@st.cache_data` for expensive data operations
- Implement proper error handling with `st.error()` and `st.warning()`
- Use `st.session_state` for maintaining state
- Optimize data queries to Databricks tables
- Use `st.spinner()` for long-running operations

#### Deployment
- Use separate targets for dev/staging/prod
- Configure appropriate permissions in bundle
- Monitor app performance and logs
- Use serverless compute when possible

#### Security
- Never hardcode credentials
- Use Databricks SDK for authentication
- Implement proper access controls
- Validate user inputs

### Common Use Cases
1. **Data Dashboards**: Real-time analytics and KPI monitoring
2. **ML Model Interfaces**: Interactive model predictions and explanations
3. **Data Quality Tools**: Data validation and monitoring interfaces
4. **Admin Panels**: Configuration and management tools
5. **Chatbots**: LLM-powered conversational interfaces

### Integration with Databricks Resources

#### Accessing Tables
```python
from databricks.sdk import WorkspaceClient
import pandas as pd

w = WorkspaceClient()
df = pd.read_sql("SELECT * FROM main.value_advisor.recommendations", 
                 con=w.sql.get_warehouse_connection())
```

#### Using Unity Catalog
```python
# List catalogs
catalogs = w.catalogs.list()

# Access specific table
table = w.tables.get(full_name="main.value_advisor.recommendations")
```

## Terraform for Databricks

### Project Structure
- Terraform configurations should be organized in `.tf` files
- Use `terraform.tfvars` for environment-specific variables
- Keep provider configuration in `provider.tf`
- Define resources in logical groupings (e.g., `compute.tf`, `storage.tf`, `jobs.tf`)

### Common Commands
```bash
# Initialize Terraform
terraform init

# Format Terraform files
terraform fmt -recursive

# Validate configuration
terraform validate

# Plan changes
terraform plan

# Apply changes
terraform apply

# Destroy infrastructure
terraform destroy
```

### Databricks Provider Configuration
```hcl
terraform {
  required_providers {
    databricks = {
      source = "databricks/databricks"
    }
  }
}

provider "databricks" {
  # Authentication configured via environment variables or config profile
}
```

## Best Practices

### Terraform
- Always run `terraform plan` before `apply`
- Use remote state storage (e.g., S3, Azure Storage) for team collaboration
- Tag all resources appropriately
- Use data sources to reference existing Databricks resources
- Implement proper workspace isolation between environments

## Authentication
- Use environment variables or Databricks CLI profiles for authentication
- Never commit credentials to version control
- For CI/CD, use service principals with appropriate permissions

## File Organization
- Keep each DAB project in its own subdirectory
- Terraform modules should be in separate directories under `terraform/`
- Share common configurations using Terraform modules or DAB templates
- For apps, maintain clear separation between app code and bundle configuration
