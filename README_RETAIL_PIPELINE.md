# Retail E-commerce Analytics Pipeline with dbldatagen

This project demonstrates a complete end-to-end data pipeline using:
- **dbldatagen**: For generating realistic synthetic retail data at scale
- **Delta Live Tables (DLT)**: For declarative ETL pipeline orchestration
- **Databricks Asset Bundles (DAB)**: For deployment and lifecycle management

## 📁 Project Structure

```
dbx-sandbox/
├── databricks.yml                              # Main bundle configuration
├── resources/
│   └── retail_pipeline.pipeline.yml            # DLT pipeline and job definitions
├── src/
│   ├── data_generation/
│   │   └── generate_retail_data.py             # Synthetic data generator
│   └── pipelines/
│       └── retail_dlt_pipeline.py              # DLT pipeline definition
└── README_RETAIL_PIPELINE.md                   # This file
```

## 🎯 What This Pipeline Does

### Data Generation (dbldatagen)
The pipeline generates realistic synthetic e-commerce data with referential integrity:

1. **Customers** (100K records)
   - Customer demographics
   - Account information
   - Loyalty tier segmentation

2. **Products** (10K records)
   - Product catalog with SKUs
   - Pricing and inventory
   - Category and brand information

3. **Orders** (500K records)
   - Transaction details
   - Payment methods
   - Order status tracking

4. **Order Items** (1M records)
   - Line item details
   - Quantities and pricing
   - Discounts applied

### Data Processing (DLT Pipeline)

The pipeline implements a **medallion architecture**:

#### 🥉 Bronze Layer (Raw Ingestion)
- Direct ingestion from synthetic data sources
- No transformations, preserving raw data
- Tables: `bronze_customers`, `bronze_products`, `bronze_orders`, `bronze_order_items`

#### 🥈 Silver Layer (Cleaned & Validated)
- Data quality expectations and validations
- Type conversions and enrichments
- Calculated fields (e.g., account age, order size)
- Tables: `silver_customers`, `silver_products`, `silver_orders`, `silver_order_items`

**Quality Checks Include:**
- ✅ Email format validation
- ✅ Price and quantity validations
- ✅ Timestamp consistency (shipped_ts > order_ts)
- ✅ Active products only
- ✅ Referential integrity checks

#### 🥇 Gold Layer (Business Analytics)
- Customer lifetime value (CLV) calculations
- Product performance metrics
- Daily sales summaries
- Category-level analytics
- Tables: `gold_customer_lifetime_value`, `gold_product_performance`, `gold_daily_sales_summary`, `gold_category_performance`

## 🚀 Getting Started

### Prerequisites

1. **Databricks CLI** installed and configured
   ```bash
   databricks --version
   ```

2. **UV package manager** (for local development)
   ```bash
   uv --version
   ```

3. **Environment variables** set:
   ```bash
   export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
   export DATABRICKS_TOKEN="your-token-here"
   ```

### Installation

1. **Install Python dependencies:**
   ```bash
   uv sync
   ```

2. **Validate the bundle:**
   ```bash
   databricks bundle validate
   ```

3. **Deploy to development:**
   ```bash
   databricks bundle deploy --target dev
   ```

## 📊 Running the Pipeline

### Step 1: Generate Synthetic Data

Run the data generator job:

```bash
databricks bundle run retail_data_generator --target dev
```

This will create Delta tables at `/tmp/retail_data/` with:
- Customers: 100,000 records
- Products: 10,000 records
- Orders: 500,000 records
- Order Items: 1,000,000 records

**Manual Execution (Alternative):**
```python
# In a Databricks notebook
%pip install dbldatagen==0.4.0.post1

%run /Workspace/path/to/src/data_generation/generate_retail_data.py
```

### Step 2: Run the DLT Pipeline

#### Option A: Via Databricks UI
1. Navigate to **Workflows** → **Delta Live Tables**
2. Find `[dev] Retail E-commerce DLT Pipeline`
3. Click **Start**

#### Option B: Via CLI
```bash
# Get the pipeline ID
databricks pipelines list | grep "Retail E-commerce DLT Pipeline"

# Start the pipeline
databricks pipelines start --pipeline-id <pipeline-id>
```

### Step 3: Explore the Results

Query the gold layer tables:

```sql
-- Customer lifetime value analysis
SELECT
  customer_segment,
  COUNT(*) as customer_count,
  ROUND(AVG(lifetime_value), 2) as avg_ltv,
  ROUND(AVG(total_orders), 2) as avg_orders
FROM bu1_dev.retail_analytics_dev.gold_customer_lifetime_value
GROUP BY customer_segment
ORDER BY avg_ltv DESC;

-- Daily sales trends
SELECT
  order_date,
  total_orders,
  total_revenue,
  avg_order_value,
  unique_customers
FROM bu1_dev.retail_analytics_dev.gold_daily_sales_summary
ORDER BY order_date DESC
LIMIT 30;

-- Category performance
SELECT
  category,
  total_revenue,
  total_units_sold,
  stock_availability_pct
FROM bu1_dev.retail_analytics_dev.gold_category_performance
ORDER BY total_revenue DESC;
```

## 🔍 Key Features Demonstrated

### dbldatagen Features
- ✅ **Referential Integrity**: Customer IDs, Product IDs, Order IDs properly linked
- ✅ **Realistic Data**: Names, emails, timestamps, prices using templates and distributions
- ✅ **Data Constraints**: SQL constraints (e.g., shipped_ts > order_ts)
- ✅ **Custom Distributions**: Normal distributions for prices, quantities
- ✅ **Weighted Values**: Country codes, payment methods with realistic weights
- ✅ **Calculated Fields**: Derived columns using expressions

### DLT Features
- ✅ **Declarative Syntax**: Python decorators (@dlt.table, @dlt.expect)
- ✅ **Data Quality**: Expectations with automatic tracking
- ✅ **Incremental Processing**: Ready for streaming with small modifications
- ✅ **Lineage Tracking**: Automatic data lineage visualization
- ✅ **Optimization**: Z-ordering for query performance
- ✅ **Serverless Compute**: No cluster management required

### DAB Features
- ✅ **Multi-Environment**: Dev/Prod configurations
- ✅ **Variables**: Parameterized catalog and schema names
- ✅ **Permissions**: Built-in access control
- ✅ **CI/CD Ready**: Git-based deployment workflow

## 🎓 Educational Insights

### Why dbldatagen?

dbldatagen is purpose-built for Databricks and offers several advantages over alternatives like Faker:

1. **Spark-Native**: Generates data directly in Spark DataFrames with proper partitioning
2. **Referential Integrity**: Built-in support for maintaining relationships across tables
3. **Performance**: Generates millions of rows efficiently using Spark's distributed processing
4. **Databricks Integration**: Optimized for Delta Lake and Unity Catalog
5. **Reproducibility**: Deterministic data generation using base columns and hash-based seeding

### Medallion Architecture Benefits

The Bronze → Silver → Gold pattern provides:

- **Bronze**: Immutable raw data for audit and reprocessing
- **Silver**: Cleaned data as the "single source of truth"
- **Gold**: Business-specific aggregations for fast analytics

### DLT Expectations

DLT expectations provide automated data quality monitoring:

- **@dlt.expect**: Track violations but allow records through
- **@dlt.expect_or_drop**: Drop records that fail validation
- **@dlt.expect_or_fail**: Fail the pipeline on violations

## 🔧 Customization

### Adjust Data Volume

Edit `src/data_generation/generate_retail_data.py`:

```python
# Configuration
num_customers = 100000      # Increase for more customers
num_products = 10000        # Increase for larger catalog
num_orders = 500000         # Increase for more transactions
num_order_items = 1000000   # Increase for more line items
```

### Add Custom Metrics

Add new gold layer tables in `src/pipelines/retail_dlt_pipeline.py`:

```python
@dlt.table(name="gold_my_custom_metric")
def gold_my_custom_metric():
    return (
        dlt.read("silver_orders")
        .groupBy("custom_field")
        .agg(...)
    )
```

### Change Target Environment

```bash
# Deploy to production
databricks bundle deploy --target prod

# Run in production
databricks bundle run retail_data_generator --target prod
```

## 📚 Additional Resources

- **dbldatagen Documentation**: https://github.com/databrickslabs/dbldatagen
- **Delta Live Tables Guide**: https://docs.databricks.com/delta-live-tables/
- **Databricks Asset Bundles**: https://docs.databricks.com/dev-tools/bundles/
- **Example Bundles**: https://github.com/databricks/bundle-examples

## 🐛 Troubleshooting

### Issue: "Table not found"
**Solution**: Ensure the data generator job has completed successfully before running the DLT pipeline.

### Issue: "Permission denied"
**Solution**: Check that your user has CREATE TABLE permissions in the target catalog and schema.

### Issue: "Library not found: dbldatagen"
**Solution**: The library is specified in the job definition. Ensure you're using the deployed bundle version.

### Issue: Pipeline validation errors
**Solution**: Run `databricks bundle validate` to check for configuration issues.

## 📝 License

This example is provided as-is for educational and demonstration purposes.

## 👥 Contributing

Feel free to extend this example with:
- Additional data quality checks
- More complex aggregations
- Streaming data sources
- ML feature engineering
- Real-time dashboards
