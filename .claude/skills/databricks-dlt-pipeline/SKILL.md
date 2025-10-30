---
name: databricks-dlt-pipeline
description: Create Databricks Delta Live Tables (DLT) pipelines using Python decorators with built-in data quality expectations. Focuses on declarative pipeline development with medallion architecture and streaming support.
version: 1.0.0
model: sonnet
---

# Databricks Delta Live Tables (DLT) Pipeline

## What This Skill Does

This skill helps you scaffold production-ready Databricks Delta Live Tables pipelines using Python decorators. It emphasizes:

- **Declarative approach**: Define *what* data transformations should happen, not *how*
- **Data quality first**: Every table includes expectations for validation and monitoring
- **Medallion architecture**: Structure data in bronze → silver → gold layers
- **Python-native**: All pipeline logic uses Python decorators and PySpark, not SQL cells
- **Functional programming**: Clean, reusable transformation functions
- **Streaming-ready**: Support for both batch and incremental processing

The skill creates pipelines that are testable, maintainable, and follow Databricks best practices.

## Prerequisites Check

Before creating a DLT pipeline, verify:

1. **Project structure exists**:
   - `src/` directory for pipeline Python files
   - `resources/` directory for DAB resource definitions
   - `databricks.yml` at project root

2. **Python environment ready**:
   - Python 3.10+ configured
   - Type hints support available
   - `uv` package manager set up (for local development)

3. **Databricks bundle configured**:
   - Bundle has at least one target (dev/staging/prod)
   - Workspace connection is valid (run `databricks bundle validate` to check)

4. **Data source identified**:
   - Know the source table/path for ingestion
   - Understand source data schema
   - Determine if source is batch or streaming

## Instructions

### Step 1: Determine Pipeline Structure

First, decide on:
- **Pipeline name**: Use snake_case (e.g., `customer_analytics`, `sales_pipeline`)
- **Location**: Which environment? (`src/dev/`, `src/staging/`, `src/prod/`)
- **Architecture**: How many layers? (Typically bronze → silver → gold)

**Example structure**:
```
src/
  dev/
    customer_pipeline.py    # Your DLT pipeline
  prod/
    customer_pipeline.py    # Production version
```

### Step 2: Create Python Pipeline File

Create a new Python file in the appropriate `src/` subdirectory. The file will contain all your DLT table and view definitions.

**File naming**: Use descriptive names like `<domain>_pipeline.py` or `<entity>_dlt.py`

### Step 3: Import Required Modules

At the top of your pipeline file, import DLT and PySpark modules:

```python
"""Customer analytics pipeline using Delta Live Tables.

This pipeline processes customer transaction data through bronze, silver,
and gold layers with data quality expectations at each stage.
"""

import dlt
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, current_timestamp, to_date
```

**Key imports**:
- `import dlt`: Delta Live Tables decorators and functions
- `from pyspark.sql import DataFrame`: Type hints
- `from pyspark.sql.functions import *`: Transformation functions

### Step 4: Define Bronze Layer (Raw Ingestion)

Create your first table/view to ingest raw data. Use `@dlt.view` for non-persisted intermediate data or `@dlt.table` for persisted datasets.

**Batch source example**:
```python
@dlt.table(
    comment="Raw customer transactions ingested from source system",
    table_properties={
        "quality": "bronze",
        "pipelines.autoOptimize.zOrderCols": "customer_id"
    }
)
@dlt.expect("has_transaction_id", "transaction_id IS NOT NULL")
def bronze_transactions() -> DataFrame:
    """Ingest raw transaction data from source system.

    Returns:
        DataFrame: Raw transaction records with basic validation
    """
    return (
        spark.read.format("parquet")
        .load("/mnt/source/transactions/")
        .withColumn("ingestion_timestamp", current_timestamp())
    )
```

**Streaming source example**:
```python
@dlt.table(
    comment="Raw events streamed from Kafka topic",
    table_properties={"quality": "bronze"}
)
@dlt.expect("has_event_id", "event_id IS NOT NULL")
def bronze_events() -> DataFrame:
    """Stream raw events from Kafka topic.

    Returns:
        DataFrame: Raw event stream with ingestion metadata
    """
    return (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", "kafka:9092")
        .option("subscribe", "customer-events")
        .load()
        .withColumn("ingestion_timestamp", current_timestamp())
    )
```

### Step 5: Add Data Quality Expectations

DLT provides three types of expectations for data quality:

1. **`@dlt.expect(name, constraint)`**: Log violations but keep records
2. **`@dlt.expect_or_drop(name, constraint)`**: Drop records that fail
3. **`@dlt.expect_or_fail(name, constraint)`**: Fail the pipeline if any record fails

**Quality expectation examples**:
```python
@dlt.table(
    comment="Validated transactions with quality expectations",
    table_properties={"quality": "silver"}
)
@dlt.expect("valid_amount", "amount > 0")  # Log violations
@dlt.expect_or_drop("valid_customer", "customer_id IS NOT NULL")  # Drop bad records
@dlt.expect_or_fail("has_timestamp", "transaction_date IS NOT NULL")  # Fail pipeline
@dlt.expect("recent_transaction", "transaction_date >= '2020-01-01'")
def silver_transactions() -> DataFrame:
    """Clean and validated transaction data.

    Applies multiple data quality expectations:
    - Amount must be positive (logged)
    - Customer ID is required (dropped if missing)
    - Transaction date is required (fails if missing)
    - Transaction must be recent (logged)

    Returns:
        DataFrame: Validated transaction records
    """
    return dlt.read("bronze_transactions")
```

**Best practices**:
- Add at least one expectation per table
- Use `expect_or_fail` for critical business rules
- Use `expect_or_drop` to filter out known bad data
- Use `expect` for monitoring and alerting
- Name expectations clearly (e.g., `valid_email`, `positive_amount`)

### Step 6: Create Transformation Layers

Build your silver and gold layers by reading from DLT datasets using `dlt.read()` or `dlt.read_stream()`.

**Silver layer (cleaned data)**:
```python
@dlt.table(
    comment="Cleaned customer transactions with business logic applied",
    table_properties={"quality": "silver"}
)
@dlt.expect_or_drop("valid_transaction_type", "transaction_type IN ('purchase', 'refund', 'adjustment')")
@dlt.expect("positive_amount", "amount > 0")
def silver_transactions_cleaned() -> DataFrame:
    """Apply business rules and data cleaning.

    Returns:
        DataFrame: Business-validated transaction records
    """
    return (
        dlt.read("bronze_transactions")
        .filter(col("transaction_id").isNotNull())
        .withColumn("transaction_date", to_date(col("timestamp")))
        .select(
            "transaction_id",
            "customer_id",
            "amount",
            "transaction_type",
            "transaction_date",
            "ingestion_timestamp"
        )
    )
```

**Gold layer (aggregated/enriched data)**:
```python
@dlt.table(
    comment="Daily customer transaction summary for analytics",
    table_properties={
        "quality": "gold",
        "delta.enableChangeDataFeed": "true"
    }
)
def gold_daily_customer_summary() -> DataFrame:
    """Aggregate transactions by customer and date.

    Returns:
        DataFrame: Daily customer metrics for reporting
    """
    return (
        dlt.read("silver_transactions_cleaned")
        .groupBy("customer_id", "transaction_date")
        .agg({
            "amount": "sum",
            "transaction_id": "count"
        })
        .withColumnRenamed("sum(amount)", "total_amount")
        .withColumnRenamed("count(transaction_id)", "transaction_count")
    )
```

**Streaming aggregation with watermarking**:
```python
@dlt.table(
    comment="Real-time customer event counts with 1-hour windows",
    table_properties={"quality": "gold"}
)
def gold_event_counts_windowed() -> DataFrame:
    """Aggregate streaming events with watermarking.

    Returns:
        DataFrame: Windowed event counts per customer
    """
    return (
        dlt.read_stream("bronze_events")
        .withWatermark("event_timestamp", "1 hour")
        .groupBy("customer_id", window(col("event_timestamp"), "1 hour"))
        .count()
    )
```

### Step 7: Add Metadata and Documentation

Enhance your tables with proper metadata:

```python
@dlt.table(
    comment="Gold layer customer lifetime value metrics",
    table_properties={
        "quality": "gold",
        "pipelines.autoOptimize.zOrderCols": "customer_id",
        "delta.enableChangeDataFeed": "true",
        "owner": "data-team",
        "domain": "customer-analytics"
    }
)
@dlt.expect("valid_ltv", "lifetime_value >= 0")
def gold_customer_ltv() -> DataFrame:
    """Calculate customer lifetime value metrics.

    Combines transaction history, refunds, and customer attributes
    to compute LTV for each customer.

    Returns:
        DataFrame: Customer LTV metrics for ML and reporting
    """
    return (
        dlt.read("silver_transactions_cleaned")
        .groupBy("customer_id")
        .agg({
            "amount": "sum",
            "transaction_date": "max"
        })
        .withColumnRenamed("sum(amount)", "lifetime_value")
        .withColumnRenamed("max(transaction_date)", "last_transaction_date")
    )
```

**Metadata best practices**:
- Use `comment` to describe table purpose
- Add `quality` property to indicate layer (bronze/silver/gold)
- Enable Change Data Feed for downstream CDC consumers
- Use Z-ordering for frequently filtered columns
- Add owner and domain tags for governance

### Step 8: Create DLT Pipeline Resource Definition

Create or update the pipeline resource in `resources/<pipeline_name>.pipeline.yml`:

```yaml
resources:
  pipelines:
    customer_analytics_pipeline:
      name: "customer_analytics_${bundle.target}"

      # Use serverless for automatic scaling
      serverless: true

      # Libraries - your pipeline Python file
      libraries:
        - notebook:
            path: ../src/${bundle.target}/customer_pipeline.py

      # Target schema and catalog
      target: customer_analytics_${bundle.target}
      catalog: ${var.catalog_name}

      # Development settings
      development: true

      # Continuous vs triggered
      continuous: false

      # Data quality enforcement
      configuration:
        "pipelines.enableTrackHistory": "true"

      # Notifications (optional)
      notifications:
        - email_recipients:
            - data-team@company.com
          alerts:
            - "on-update-failure"
            - "on-flow-failure"
```

**Key configuration**:
- `serverless: true`: Use serverless compute (recommended)
- `development: true`: Enable development mode for faster iterations
- `continuous: false`: Run on-demand (set `true` for streaming)
- `catalog` and `target`: Unity Catalog location

### Step 9: Configure Bundle Target

Ensure your `databricks.yml` includes the pipeline resource:

```yaml
bundle:
  name: customer_analytics

include:
  - resources/*.yml

targets:
  dev:
    mode: development
    workspace:
      host: https://your-workspace.databricks.com
    variables:
      catalog_name: dev_catalog

  prod:
    mode: production
    workspace:
      host: https://your-workspace.databricks.com
    variables:
      catalog_name: prod_catalog
```

### Step 10: Validate and Deploy

```bash
# Validate the bundle
databricks bundle validate --target dev

# Deploy the pipeline
databricks bundle deploy --target dev

# Start the pipeline
databricks bundle run customer_analytics_pipeline --target dev
```

## Success Criteria

Your DLT pipeline is successfully created when:

- ✅ Python file created with proper DLT decorators (`@dlt.table`, `@dlt.view`)
- ✅ All functions have type hints and return `DataFrame`
- ✅ All functions have docstrings following PEP 257
- ✅ At least one data quality expectation per table
- ✅ Medallio architecture implemented (bronze → silver → gold)
- ✅ Pipeline resource defined in `resources/` directory
- ✅ Bundle validates without errors: `databricks bundle validate`
- ✅ Code follows functional programming principles (pure functions)
- ✅ Tables have descriptive comments and metadata
- ✅ Proper use of `dlt.read()` or `dlt.read_stream()` for referencing datasets

## Error Handling

### Common Issues and Solutions

**1. "AnalysisException: Table or view not found"**
```
Cause: Referenced DLT dataset doesn't exist or has typo
Solution: Verify dataset name matches exactly (case-sensitive)
          Use dlt.read('exact_function_name')
```

**2. "Circular dependency detected"**
```
Cause: Tables reference each other in a loop
Solution: Restructure transformations to create clear dependency DAG
          Bronze → Silver → Gold should be unidirectional
```

**3. "Expectation failed: <expectation_name>"**
```
Cause: Data quality expectation is failing
Solution: - If using @dlt.expect_or_fail: Fix data or relax constraint
          - If using @dlt.expect_or_drop: Check dropped record metrics
          - Review expectation logic for correctness
```

**4. "Cannot import name 'dlt'"**
```
Cause: DLT only available in Databricks runtime, not local Python
Solution: This is expected - pipeline runs in Databricks, not locally
          For local testing, mock dlt or use databricks-connect
```

**5. "Bundle validation failed"**
```
Cause: YAML syntax error or invalid resource configuration
Solution: Check resources/*.yml syntax
          Validate path references are correct
          Ensure all required fields are present
```

**6. "Stream-static join without watermark"**
```
Cause: Joining streaming data without proper watermarking
Solution: Add .withWatermark("timestamp_col", "interval") before joins
          Example: .withWatermark("event_time", "1 hour")
```

## Additional Notes

### Best Practices

1. **Start simple, iterate**: Begin with basic bronze → silver → gold, then add complexity
2. **Use views for ephemeral data**: `@dlt.view` for intermediate transformations you don't need to persist
3. **Use tables for checkpoints**: `@dlt.table` for recovery points and important artifacts
4. **Streaming first**: If data is incremental, use streaming from the start—easier to scale
5. **Test expectations**: Start with `@dlt.expect` to monitor, then upgrade to `expect_or_drop/fail`
6. **Leverage serverless**: Default to serverless compute for automatic scaling and cost optimization
7. **Version your pipelines**: Use separate directories (dev/staging/prod) for environment isolation

### Performance Tips

- Enable Auto Optimize with Z-ordering on filter columns
- Use partitioning for large tables (`partitionedBy`)
- Configure appropriate trigger intervals for streaming
- Use broadcast joins for small dimension tables
- Enable Change Data Feed for downstream incremental consumers

### Testing Strategy

1. **Unit tests**: Test transformation logic locally with sample data
2. **Integration tests**: Deploy to dev environment with subset of data
3. **Data quality monitoring**: Review expectation metrics in DLT UI
4. **Schema evolution**: Test with representative schema changes
5. **Performance testing**: Validate with production-scale data volumes

### Documentation References

- **DLT Python Reference**: https://docs.databricks.com/delta-live-tables/python-ref.html
- **Data Quality Expectations**: https://docs.databricks.com/delta-live-tables/expectations.html
- **DLT Properties**: https://docs.databricks.com/delta-live-tables/properties.html
- **Streaming in DLT**: https://docs.databricks.com/delta-live-tables/streaming.html
- **Bundle Examples**: https://github.com/databricks/bundle-examples
- **DLT Best Practices**: https://docs.databricks.com/delta-live-tables/best-practices.html

### Pattern Library

**Slowly Changing Dimension (SCD Type 2)**:
```python
@dlt.table
def silver_customer_scd() -> DataFrame:
    """Track customer attribute changes over time (SCD Type 2)."""
    return (
        dlt.read_stream("bronze_customers")
        .select(
            "customer_id",
            "name",
            "email",
            "status",
            col("updated_at").alias("valid_from"),
            lit(None).alias("valid_to"),
            lit(True).alias("is_current")
        )
    )
```

**Incremental Deduplication**:
```python
@dlt.table
def silver_events_deduped() -> DataFrame:
    """Deduplicate events based on event_id, keeping latest."""
    from pyspark.sql.window import Window

    window_spec = Window.partitionBy("event_id").orderBy(col("ingestion_timestamp").desc())

    return (
        dlt.read("bronze_events")
        .withColumn("row_num", row_number().over(window_spec))
        .filter(col("row_num") == 1)
        .drop("row_num")
    )
```

**Join with Reference Data**:
```python
@dlt.table
def gold_enriched_transactions() -> DataFrame:
    """Enrich transactions with customer and product dimensions."""
    return (
        dlt.read("silver_transactions")
        .join(
            dlt.read("dim_customers"),
            "customer_id",
            "left"
        )
        .join(
            dlt.read("dim_products"),
            "product_id",
            "left"
        )
    )
```

---

**Remember**: The goal is to create pipelines that are simple, reliable, and maintainable. Start with the basics, add data quality expectations early, and iterate based on actual data patterns and business needs.
