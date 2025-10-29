---
name: databricks-mcp-setup
description: Create a new Databricks MCP server project with FastAPI + FastMCP integration for building AI-powered Databricks workspace management tools. Use when creating MCP servers for Databricks, setting up cluster management tools, SQL execution, job orchestration, Unity Catalog operations, or deploying to Databricks Apps.
version: 1.0.0
---

# Databricks MCP Server Setup

Create a new Databricks MCP server project with FastAPI + FastMCP integration for building AI-powered Databricks workspace management tools.

## What This Skill Does

This skill automates the creation of a complete Databricks MCP server project including:
- Project structure with best practices
- FastAPI + FastMCP application setup
- Example Databricks tools (clusters, SQL execution)
- Prompt loading system
- Configuration files for local development and Databricks Apps deployment
- Testing scripts and development utilities
- Complete documentation

## Prerequisites Check

Before running this skill, verify you have:
- Python 3.11 or higher installed
- `uv` package manager installed (https://github.com/astral-sh/uv)
- Databricks CLI installed (`pip install databricks-cli`)
- Databricks workspace access with a Personal Access Token
- (Optional) Node.js 18+ and Bun for frontend development

## Instructions

### Step 1: Gather Project Information

Ask the user for the following information:

1. **Project name** (default: "my-databricks-mcp")
   - Used for directory name and package name
   - Should be lowercase with hyphens (e.g., "sales-analytics-mcp")

2. **MCP server name** (default: same as project name)
   - Name that will appear in Claude and other MCP clients
   - Can be more descriptive (e.g., "Sales Analytics for Databricks")

3. **Initial tools to include** (checkboxes):
   - [ ] Cluster management (list, get, create, start, terminate)
   - [ ] SQL execution (execute queries on SQL warehouses)
   - [ ] Job management (list, run, get status)
   - [ ] Unity Catalog (list catalogs, schemas, tables)
   - [ ] Workspace operations (list notebooks, export)
   - [ ] DBFS operations (list, read, write files)

4. **Databricks workspace URL** (e.g., "https://your-workspace.cloud.databricks.com")
   - Used in .env.local template

5. **Include frontend** (yes/no, default: no)
   - Creates React + Vite frontend scaffold if yes

### Step 2: Create Project Structure

Create the following directory structure:

```
{project_name}/
├── server/
│   ├── __init__.py
│   ├── app.py
│   ├── tools.py
│   ├── prompts.py
│   ├── routers/
│   │   ├── __init__.py
│   │   └── health.py
│   └── services/
│       ├── __init__.py
│       ├── databricks_client.py
│       └── utils.py
├── prompts/
│   └── .gitkeep
├── tests/
│   ├── __init__.py
│   └── test_tools.py
├── scripts/
│   ├── watch.sh
│   ├── deploy.sh
│   ├── fix.sh
│   └── setup.sh
├── claude_scripts/
│   ├── inspect_local_mcp.sh
│   ├── test_local_mcp_curl.sh
│   └── test_remote_mcp_curl.sh
├── .env.local
├── config.yaml
├── app.yaml
├── pyproject.toml
├── .gitignore
└── README.md
```

If include_frontend is yes, also create:
```
{project_name}/
├── client/
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
```

### Step 3: Generate Files

#### 3.1 Create pyproject.toml

```toml
[project]
name = "{project_name}"
version = "0.1.0"
description = "MCP server for Databricks integration"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.104.1",
    "uvicorn[standard]>=0.24.0",
    "databricks-sdk==0.59.0",
    "fastmcp>=0.2.0",
    "mcp>=1.12.0",
    "pyyaml>=6.0.2",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "ruff>=0.1.0",
]

[project.scripts]
dbx-mcp-proxy = "server.proxy:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]
```

#### 3.2 Create server/services/databricks_client.py

```python
import os
from databricks.sdk import WorkspaceClient
from databricks.sdk.errors import DatabricksError

def get_workspace_client() -> WorkspaceClient:
    """Get authenticated Databricks workspace client.

    Uses environment variables:
    - DATABRICKS_HOST: Workspace URL
    - DATABRICKS_TOKEN: Personal access token or auto-injected by Databricks Apps
    """
    return WorkspaceClient(
        host=os.environ.get('DATABRICKS_HOST'),
        token=os.environ.get('DATABRICKS_TOKEN')
    )

def verify_authentication() -> dict:
    """Verify Databricks authentication is working."""
    try:
        client = get_workspace_client()
        user = client.current_user.me()
        return {
            'success': True,
            'user_name': user.user_name,
            'user_id': user.id,
            'workspace_url': client.config.host
        }
    except DatabricksError as e:
        return {
            'success': False,
            'error': f'Authentication failed: {str(e)}'
        }
```

#### 3.3 Create server/services/utils.py

```python
def success_response(data=None, message=None, count=None, **metadata):
    """Create standardized success response."""
    response = {'success': True}

    if data is not None:
        response['data'] = data

    if count is not None:
        response['count'] = count
    elif isinstance(data, list):
        response['count'] = len(data)

    if message:
        response['message'] = message

    if metadata:
        response['metadata'] = metadata

    return response


def error_response(error, error_code='OPERATION_FAILED', suggestion=None, details=None):
    """Create standardized error response."""
    response = {
        'success': False,
        'error': str(error),
        'error_code': error_code
    }

    if suggestion:
        response['suggestion'] = suggestion

    if details:
        response['details'] = details

    return response
```

#### 3.4 Create server/tools.py

Generate tools based on user selections. Always include a basic example tool.

**Base structure:**

```python
import os
from databricks.sdk.errors import DatabricksError, NotFound, PermissionDenied
from server.services.databricks_client import get_workspace_client
from server.services.utils import success_response, error_response

def load_tools(mcp_server):
    """Register all MCP tools with the server."""

    # [INCLUDE SELECTED TOOLS HERE]
```

**If "Cluster management" selected, include:**

```python
    @mcp_server.tool
    def list_clusters() -> dict:
        """List all Databricks clusters in the workspace.

        Returns comprehensive cluster information including:
        - Cluster ID and name
        - Current state (RUNNING, TERMINATED, etc.)
        - Size (number of workers)
        - Spark version and node types
        - Creator and creation time

        Returns:
            Dictionary with success status and list of clusters
        """
        try:
            client = get_workspace_client()
            clusters = []

            for cluster in client.clusters.list():
                clusters.append({
                    'cluster_id': cluster.cluster_id,
                    'cluster_name': cluster.cluster_name,
                    'state': cluster.state.value if cluster.state else 'UNKNOWN',
                    'num_workers': cluster.num_workers,
                    'spark_version': cluster.spark_version,
                    'node_type_id': cluster.node_type_id,
                    'creator_user_name': cluster.creator_user_name,
                })

            return success_response(data={'clusters': clusters}, count=len(clusters))

        except PermissionDenied:
            return error_response(
                'Permission denied to list clusters',
                'PERMISSION_DENIED',
                suggestion='Ensure you have cluster read permissions in your workspace'
            )
        except DatabricksError as e:
            return error_response(str(e), 'DATABRICKS_ERROR')
        except Exception as e:
            return error_response(f'Unexpected error: {str(e)}', 'INTERNAL_ERROR')

    @mcp_server.tool
    def get_cluster(cluster_id: str) -> dict:
        """Get detailed information about a specific cluster."""
        try:
            client = get_workspace_client()
            cluster = client.clusters.get(cluster_id=cluster_id)

            return success_response(data={
                'cluster_id': cluster.cluster_id,
                'cluster_name': cluster.cluster_name,
                'state': cluster.state.value if cluster.state else 'UNKNOWN',
                'num_workers': cluster.num_workers,
                'spark_version': cluster.spark_version,
                'node_type_id': cluster.node_type_id,
                'creator_user_name': cluster.creator_user_name,
                'spark_conf': cluster.spark_conf,
            })

        except NotFound:
            return error_response(
                f'Cluster {cluster_id} not found',
                'NOT_FOUND',
                suggestion='Verify the cluster ID and try again'
            )
        except DatabricksError as e:
            return error_response(str(e), 'DATABRICKS_ERROR')
```

**If "SQL execution" selected, include:**

```python
    @mcp_server.tool
    def execute_sql(
        query: str,
        warehouse_id: str = None,
        catalog: str = None,
        schema: str = None
    ) -> dict:
        """Execute a SQL query on Databricks SQL warehouse.

        Args:
            query: SQL statement to execute
            warehouse_id: SQL warehouse ID (optional, uses env var if not provided)
            catalog: Unity Catalog catalog name (optional)
            schema: Schema/database name (optional)

        Returns:
            Dictionary with query results including columns, rows, and row count
        """
        try:
            client = get_workspace_client()

            if not warehouse_id:
                warehouse_id = os.environ.get('DATABRICKS_WAREHOUSE_ID')
                if not warehouse_id:
                    return error_response(
                        'No warehouse_id provided and DATABRICKS_WAREHOUSE_ID not set',
                        'MISSING_WAREHOUSE_ID',
                        suggestion='Provide warehouse_id or set DATABRICKS_WAREHOUSE_ID environment variable'
                    )

            response = client.statement_execution.execute_statement(
                warehouse_id=warehouse_id,
                statement=query,
                catalog=catalog,
                schema=schema,
                wait_timeout='30s'
            )

            if response.result and response.result.data_array:
                columns = [col.name for col in response.manifest.schema.columns]
                rows = []
                for row_data in response.result.data_array:
                    row_dict = {col: row_data[i] for i, col in enumerate(columns)}
                    rows.append(row_dict)

                return success_response(
                    data={'columns': columns, 'rows': rows},
                    count=len(rows),
                    statement_id=response.statement_id
                )
            else:
                return success_response(
                    message='Query executed successfully (no results returned)',
                    statement_id=response.statement_id
                )

        except DatabricksError as e:
            return error_response(str(e), 'DATABRICKS_ERROR', details={'query': query})
```

**If "Unity Catalog" selected, include:**

```python
    @mcp_server.tool
    def list_catalogs() -> dict:
        """List all Unity Catalog catalogs."""
        try:
            client = get_workspace_client()
            catalogs = []

            for catalog in client.catalogs.list():
                catalogs.append({
                    'name': catalog.name,
                    'comment': catalog.comment,
                    'owner': catalog.owner,
                })

            return success_response(data={'catalogs': catalogs}, count=len(catalogs))

        except DatabricksError as e:
            return error_response(str(e), 'DATABRICKS_ERROR')

    @mcp_server.tool
    def list_schemas(catalog_name: str) -> dict:
        """List schemas in a Unity Catalog catalog."""
        try:
            client = get_workspace_client()
            schemas = []

            for schema in client.schemas.list(catalog_name=catalog_name):
                schemas.append({
                    'name': schema.name,
                    'catalog_name': schema.catalog_name,
                    'comment': schema.comment,
                    'owner': schema.owner,
                })

            return success_response(data={'schemas': schemas}, count=len(schemas))

        except DatabricksError as e:
            return error_response(str(e), 'DATABRICKS_ERROR')
```

#### 3.5 Create server/prompts.py

```python
import glob
import os

def load_prompts(mcp_server):
    """Dynamically load prompts from the prompts directory."""
    prompt_dir = 'prompts'

    if not os.path.exists(prompt_dir):
        print(f"Warning: {prompt_dir} directory not found")
        return

    prompt_files = glob.glob(f'{prompt_dir}/*.md')

    for prompt_file in prompt_files:
        prompt_name = os.path.splitext(os.path.basename(prompt_file))[0]

        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.strip().split('\n')
        title = lines[0].strip().lstrip('#').strip() if lines else prompt_name

        def make_prompt_handler(prompt_content, name, desc):
            @mcp_server.prompt(name=name, description=desc)
            async def handle_prompt():
                return prompt_content
            return handle_prompt

        make_prompt_handler(content, prompt_name, title)
        print(f"Loaded prompt: {prompt_name}")
```

#### 3.6 Create server/app.py

```python
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP
import yaml

from server.tools import load_tools
from server.prompts import load_prompts

# Load environment variables for local development
env_file = Path('.env.local')
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)

# Load configuration
config = yaml.safe_load(open('config.yaml')) if os.path.exists('config.yaml') else {}
servername = config.get('servername', '{mcp_server_name}')

# Create MCP server
mcp_server = FastMCP(name=servername)

# Register tools and prompts
load_tools(mcp_server)
load_prompts(mcp_server)

# Create ASGI app for MCP
mcp_asgi_app = mcp_server.http_app()

# Create FastAPI app
app = FastAPI(
    title="{mcp_server_name}",
    description="MCP server for Databricks workspace management",
    version="0.1.0",
    lifespan=mcp_asgi_app.lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get('/api/health')
def health_check():
    """Check if server and Databricks connection are healthy."""
    from server.services.databricks_client import verify_authentication
    auth_status = verify_authentication()
    return {
        'status': 'healthy' if auth_status['success'] else 'unhealthy',
        'databricks': auth_status
    }

# Combine MCP and FastAPI routes
combined_app = FastAPI(
    title="Combined MCP App",
    routes=[
        *mcp_asgi_app.routes,
        *app.routes,
    ],
    lifespan=mcp_asgi_app.lifespan,
)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get('DATABRICKS_APP_PORT', 8000))
    uvicorn.run(combined_app, host="0.0.0.0", port=port)
```

#### 3.7 Create config.yaml

```yaml
servername: {mcp_server_name}
```

#### 3.8 Create .env.local

```bash
# Databricks authentication
DATABRICKS_HOST={databricks_workspace_url}
DATABRICKS_TOKEN=dapiXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Optional: Default SQL warehouse
DATABRICKS_WAREHOUSE_ID=

# Server configuration
DATABRICKS_APP_PORT=8000
LOG_LEVEL=INFO
```

#### 3.9 Create app.yaml

```yaml
command: ["python", "-m", "server.app"]

source_code_path: "."

environment:
  - name: DATABRICKS_HOST
    value_from: workspace

  - name: DATABRICKS_TOKEN
    value_from: pat

  - name: DATABRICKS_APP_PORT
    value_from: app_port

  - name: LOG_LEVEL
    value: INFO
```

#### 3.10 Create .gitignore

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv
.uv

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/

# Distribution
dist/
build/
*.egg-info/

# Databricks
.databricks/

# Requirements
requirements.txt
```

#### 3.11 Create scripts/watch.sh

```bash
#!/bin/bash
source .env.local
export DATABRICKS_HOST
export DATABRICKS_TOKEN
uv run uvicorn server.app:combined_app --reload --port 8000
```

#### 3.12 Create scripts/fix.sh

```bash
#!/bin/bash
uv run ruff format server/ tests/
uv run ruff check --fix server/ tests/
```

#### 3.13 Create scripts/deploy.sh

```bash
#!/bin/bash
set -e

echo "🚀 Deploying to Databricks Apps..."

source .env.local

echo "📦 Generating requirements.txt..."
uv pip compile pyproject.toml -o requirements.txt

echo "🔧 Deploying application..."
databricks apps deploy {project_name} \
    --source-code-path . \
    --config-file app.yaml

echo "✅ Deployment complete!"
APP_URL=$(databricks apps get {project_name} --json | jq -r '.url')
echo "🌐 App URL: $APP_URL"
echo "🔗 MCP Endpoint: $APP_URL/mcp/"
echo "📊 Logs: $APP_URL/logz"
```

#### 3.14 Create scripts/setup.sh

```bash
#!/bin/bash
set -e

echo "🔧 Setting up {project_name}..."

# Install Python dependencies
echo "📦 Installing dependencies with uv..."
uv sync

# Make scripts executable
chmod +x scripts/*.sh
chmod +x claude_scripts/*.sh

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env.local with your Databricks credentials"
echo "2. Run './scripts/watch.sh' to start the development server"
echo "3. Run './claude_scripts/inspect_local_mcp.sh' to test with MCP Inspector"
```

#### 3.15 Create claude_scripts/inspect_local_mcp.sh

```bash
#!/bin/bash
source .env.local
export DATABRICKS_HOST
export DATABRICKS_TOKEN

npx @modelcontextprotocol/inspector \
  uv run uvicorn server.app:combined_app --port 8000
```

#### 3.16 Create claude_scripts/test_local_mcp_curl.sh

```bash
#!/bin/bash
source .env.local
export DATABRICKS_HOST
export DATABRICKS_TOKEN

uv run uvicorn server.app:combined_app --port 8000 &
SERVER_PID=$!
sleep 3

echo "Testing MCP server..."

echo "1. Initialize session"
curl -s -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "test-client"}
    }
  }' | jq '.'

echo -e "\n2. List tools"
curl -s -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list"
  }' | jq '.result.tools[] | {name: .name, description: .description}'

kill $SERVER_PID
```

#### 3.17 Create README.md

Create a project-specific README that includes:
- Project description
- Setup instructions referencing ./scripts/setup.sh
- Development workflow (watch.sh, fix.sh)
- Testing instructions
- Deployment instructions
- Link to the main guide at /Users/robby.kiskanyan/dev/mcp/projects/databricks-mcp-guide/README.md

### Step 4: Initialize Project

After creating all files:

```bash
cd {project_name}

# Make scripts executable
chmod +x scripts/*.sh
chmod +x claude_scripts/*.sh

# Initialize uv
uv init

# Install dependencies
uv sync
```

### Step 5: Verification

Run the following checks:

1. **Directory structure**: Verify all directories and files were created
2. **Python syntax**: Run `uv run python -m py_compile server/app.py`
3. **Tool registration**: Check that tools are properly decorated
4. **Environment template**: Verify .env.local has placeholder values

### Step 6: Provide Next Steps to User

After successful creation, provide the user with:

```markdown
✅ Project '{project_name}' created successfully!

## Next Steps

1. **Configure Databricks credentials**:
   ```bash
   cd {project_name}
   # Edit .env.local with your workspace URL and token
   ```

2. **Start development server**:
   ```bash
   ./scripts/watch.sh
   ```

3. **Test with MCP Inspector** (in another terminal):
   ```bash
   ./claude_scripts/inspect_local_mcp.sh
   ```

4. **Deploy to Databricks Apps** (when ready):
   ```bash
   ./scripts/deploy.sh
   ```

## Project Structure

- `server/` - Python application code
  - `app.py` - FastAPI + FastMCP entry point
  - `tools.py` - MCP tool definitions
  - `services/` - Databricks SDK wrappers
- `prompts/` - Markdown prompt files
- `scripts/` - Development and deployment scripts
- `tests/` - Test suite

## Documentation

- **Full guide**: /Users/robby.kiskanyan/dev/mcp/projects/databricks-mcp-guide/README.md
- **Development patterns**: /Users/robby.kiskanyan/dev/mcp/projects/databricks-mcp-guide/CLAUDE.md

## Tools Included

{List the tools that were selected}

## Need Help?

- Run `./claude_scripts/test_local_mcp_curl.sh` to test without MCP client
- Check logs in the terminal running `watch.sh`
- See troubleshooting section in the main guide
```

## Error Handling

If any step fails:

1. **Directory already exists**: Ask if user wants to:
   - Delete and recreate
   - Merge/update files
   - Cancel operation

2. **Missing dependencies**:
   - Check that `uv` is installed
   - Verify Python version >= 3.11
   - Suggest: `curl -LsSf https://astral.sh/uv/install.sh | sh`

3. **Invalid project name**:
   - Must be lowercase with hyphens
   - No spaces or special characters
   - Suggest valid alternatives

4. **File write errors**:
   - Check directory permissions
   - Verify disk space
   - Try with `sudo` if needed

## Success Criteria

The skill has succeeded when:

✅ All directories and files created successfully
✅ pyproject.toml is valid and dependencies are specified
✅ All tools are properly registered with @mcp_server.tool decorator
✅ Scripts are executable (chmod +x)
✅ .env.local template is created with placeholders
✅ README.md provides clear next steps
✅ User can run `./scripts/watch.sh` and see server start

## Additional Notes

- **Keep it simple**: Don't add unnecessary complexity
- **Follow patterns**: Use the exact patterns from the research
- **Test locally first**: Encourage local testing before deployment
- **Security**: Never commit .env.local or tokens to git
- **Documentation**: Link to the comprehensive guide for details

This skill creates a production-ready starting point that users can immediately test and customize for their needs.
