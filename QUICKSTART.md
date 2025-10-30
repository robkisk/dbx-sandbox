# Quick Start Guide - Retail DLT Pipeline with dbldatagen

## 🚀 Deployment Steps

### 1. Validate the Bundle
```bash
databricks bundle validate --target dev
```

### 2. Deploy to Databricks
```bash
databricks bundle deploy --target dev
```

### 3. Generate Synthetic Data
```bash
# Run the data generator job
databricks bundle run retail_data_generator --target dev
```

**Or manually in Databricks:**
- Navigate to **Workflows** → **Jobs**
- Find `[dev] Retail Data Generator`
- Click **Run Now**

### 4. Run the DLT Pipeline

**Via Databricks UI:**
1. Go to **Workflows** → **Delta Live Tables**
2. Find `[dev] Retail E-commerce DLT Pipeline`
3. Click **Start**

**Via CLI:**
```bash
# Get pipeline ID
databricks pipelines list | grep "Retail E-commerce DLT Pipeline"

# Start the pipeline (replace <pipeline-id>)
databricks pipelines start --pipeline-id <pipeline-id>
```

### 5. Query the Results

```sql
-- Use the target catalog and schema
USE CATALOG bu1_dev;
USE SCHEMA retail_analytics_dev;

-- View customer lifetime value
SELECT * FROM gold_customer_lifetime_value LIMIT 10;

-- View daily sales summary
SELECT * FROM gold_daily_sales_summary ORDER BY order_date DESC LIMIT 30;

-- View product performance
SELECT * FROM gold_product_performance ORDER BY total_revenue DESC LIMIT 20;

-- View category performance
SELECT * FROM gold_category_performance;
```

## 📊 Generated Data Summary

| Table | Records | Description |
|-------|---------|-------------|
| Customers | 100,000 | Customer profiles with demographics |
| Products | 10,000 | Product catalog with pricing |
| Orders | 500,000 | Order transactions |
| Order Items | 1,000,000 | Line item details |

## 🏗️ Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    dbldatagen                                │
│          Synthetic Data Generator                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │   BRONZE LAYER         │
        │   - bronze_customers   │
        │   - bronze_products    │
        │   - bronze_orders      │
        │   - bronze_order_items │
        └────────┬───────────────┘
                 │
                 ▼
        ┌────────────────────────┐
        │   SILVER LAYER         │
        │   + Data Quality       │
        │   + Validations        │
        │   + Enrichments        │
        └────────┬───────────────┘
                 │
                 ▼
        ┌────────────────────────┐
        │   GOLD LAYER           │
        │   - CLV Metrics        │
        │   - Daily Sales        │
        │   - Product Perf       │
        │   - Category Perf      │
        └────────────────────────┘
```

## 🔍 Key Features

### dbldatagen
✅ Referential integrity across tables
✅ Realistic distributions (normal, weighted)
✅ SQL constraints (shipped_ts > order_ts)
✅ Templates for emails, names, SKUs
✅ Configurable data volumes

### Delta Live Tables
✅ Declarative Python syntax
✅ Automatic data quality tracking
✅ Built-in lineage visualization
✅ Serverless compute
✅ Incremental processing ready

### Databricks Asset Bundles
✅ Multi-environment (dev/prod)
✅ Git-based deployment
✅ Infrastructure as code
✅ Parameterized configurations

## 🎯 Next Steps

1. **Explore the Data**: Run queries on the gold tables
2. **Create Visualizations**: Build dashboards in Databricks SQL
3. **Customize Pipeline**: Add your own transformations
4. **Add Tests**: Implement data quality tests
5. **Schedule Jobs**: Set up automated runs

## 📚 Documentation

See [README_RETAIL_PIPELINE.md](./README_RETAIL_PIPELINE.md) for full documentation.
