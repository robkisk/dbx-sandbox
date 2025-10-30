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
- use the following for any additional research related to creating a SKILL.md file: https://www.anthropic.com/news/skills