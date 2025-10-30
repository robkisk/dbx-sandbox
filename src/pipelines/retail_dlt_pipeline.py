# Databricks notebook source
"""Delta Live Tables Pipeline for Retail E-commerce Data.

This DLT pipeline demonstrates a multi-layer medallion architecture:
- Bronze: Raw data ingestion from synthetic data sources
- Silver: Cleaned and validated data with quality checks
- Gold: Business-level aggregations and analytics

The pipeline includes:
- Data quality expectations
- Referential integrity checks
- Type conversions and validations
- Business KPIs and metrics
"""

# COMMAND ----------

import dlt
from pyspark.sql.functions import (
    col,
    count,
    current_timestamp,
    date_format,
    datediff,
    max,
    min,
    round,
    sum,
    when,
)

# COMMAND ----------

# MAGIC %md
# MAGIC # Bronze Layer - Raw Data Ingestion
# MAGIC
# MAGIC Ingest raw synthetic data from Delta tables without transformations

# COMMAND ----------

@dlt.table(
    name="bronze_customers",
    comment="Raw customer data ingested from synthetic data generator",
    table_properties={"quality": "bronze", "pipelines.autoOptimize.zOrderCols": "customer_id"},
)
def bronze_customers():
    """Ingest raw customer data from Delta tables."""
    return spark.read.format("delta").load("/tmp/retail_data/customers")


@dlt.table(
    name="bronze_products",
    comment="Raw product catalog data",
    table_properties={"quality": "bronze", "pipelines.autoOptimize.zOrderCols": "product_id"},
)
def bronze_products():
    """Ingest raw product data from Delta tables."""
    return spark.read.format("delta").load("/tmp/retail_data/products")


@dlt.table(
    name="bronze_orders",
    comment="Raw order transaction data",
    table_properties={"quality": "bronze", "pipelines.autoOptimize.zOrderCols": "order_id"},
)
def bronze_orders():
    """Ingest raw order data from Delta tables."""
    return spark.read.format("delta").load("/tmp/retail_data/orders")


@dlt.table(
    name="bronze_order_items",
    comment="Raw order line items data",
    table_properties={"quality": "bronze", "pipelines.autoOptimize.zOrderCols": "order_id"},
)
def bronze_order_items():
    """Ingest raw order items data from Delta tables."""
    return spark.read.format("delta").load("/tmp/retail_data/order_items")

# COMMAND ----------

# MAGIC %md
# MAGIC # Silver Layer - Cleaned and Validated Data
# MAGIC
# MAGIC Apply data quality checks, validations, and enrichments

# COMMAND ----------

@dlt.table(
    name="silver_customers",
    comment="Cleaned and validated customer data with quality checks",
    table_properties={
        "quality": "silver",
        "pipelines.autoOptimize.zOrderCols": "customer_id",
    },
)
@dlt.expect_all(
    {
        "valid_customer_id": "customer_id IS NOT NULL",
        "valid_email": "email IS NOT NULL AND email LIKE '%@%'",
        "valid_country": "country IS NOT NULL",
        "valid_created_timestamp": "account_created_ts IS NOT NULL",
    }
)
def silver_customers():
    """Clean and validate customer data with quality expectations."""
    return (
        dlt.read("bronze_customers")
        .withColumn("email_domain", col("email").substr(col("email").cast("string").indexOf("@") + 2, 100))
        .withColumn("account_age_days", datediff(current_timestamp(), col("account_created_ts")))
        .withColumn("ingestion_timestamp", current_timestamp())
    )


@dlt.table(
    name="silver_products",
    comment="Cleaned and validated product catalog",
    table_properties={
        "quality": "silver",
        "pipelines.autoOptimize.zOrderCols": "product_id,category",
    },
)
@dlt.expect_all(
    {
        "valid_product_id": "product_id IS NOT NULL",
        "valid_sku": "product_sku IS NOT NULL",
        "valid_price": "unit_price > 0",
        "valid_stock": "stock_quantity >= 0",
    }
)
@dlt.expect_or_drop("active_products_only", "is_active = 'Y'")
def silver_products():
    """Clean and validate product data, keeping only active products."""
    return (
        dlt.read("bronze_products")
        .withColumn(
            "price_category",
            when(col("unit_price") < 20, "budget")
            .when(col("unit_price") < 100, "mid-range")
            .when(col("unit_price") < 500, "premium")
            .otherwise("luxury"),
        )
        .withColumn(
            "stock_status",
            when(col("stock_quantity") == 0, "out_of_stock")
            .when(col("stock_quantity") < 10, "low_stock")
            .otherwise("in_stock"),
        )
        .withColumn("ingestion_timestamp", current_timestamp())
    )


@dlt.table(
    name="silver_orders",
    comment="Cleaned and validated order transactions",
    table_properties={
        "quality": "silver",
        "pipelines.autoOptimize.zOrderCols": "order_id,customer_id,order_ts",
    },
)
@dlt.expect_all(
    {
        "valid_order_id": "order_id IS NOT NULL",
        "valid_customer_id": "customer_id IS NOT NULL",
        "valid_order_timestamp": "order_ts IS NOT NULL",
        "valid_amounts": "total_amount > 0 AND subtotal > 0",
        "valid_tax": "tax_amount >= 0",
        "valid_shipping": "shipping_cost >= 0",
        "valid_shipped_timestamp": "shipped_ts IS NULL OR shipped_ts >= order_ts",
    }
)
def silver_orders():
    """Clean and validate order data with business rules."""
    return (
        dlt.read("bronze_orders")
        .withColumn("order_date", date_format(col("order_ts"), "yyyy-MM-dd"))
        .withColumn("order_year", date_format(col("order_ts"), "yyyy"))
        .withColumn("order_month", date_format(col("order_ts"), "yyyy-MM"))
        .withColumn("order_quarter", date_format(col("order_ts"), "yyyy-QQ"))
        .withColumn(
            "fulfillment_days",
            when(col("shipped_ts").isNotNull(), datediff(col("shipped_ts"), col("order_ts"))).otherwise(None),
        )
        .withColumn(
            "order_size",
            when(col("total_amount") < 50, "small")
            .when(col("total_amount") < 200, "medium")
            .when(col("total_amount") < 500, "large")
            .otherwise("xlarge"),
        )
        .withColumn("ingestion_timestamp", current_timestamp())
    )


@dlt.table(
    name="silver_order_items",
    comment="Cleaned and validated order line items with product enrichment",
    table_properties={
        "quality": "silver",
        "pipelines.autoOptimize.zOrderCols": "order_id,product_id",
    },
)
@dlt.expect_all(
    {
        "valid_order_item_id": "order_item_id IS NOT NULL",
        "valid_order_id": "order_id IS NOT NULL",
        "valid_product_id": "product_id IS NOT NULL",
        "valid_quantity": "quantity > 0",
        "valid_unit_price": "unit_price > 0",
        "valid_line_total": "line_total > 0",
        "valid_discount": "discount_amount >= 0",
    }
)
def silver_order_items():
    """Clean and validate order items with calculated fields."""
    return (
        dlt.read("bronze_order_items")
        .withColumn("effective_unit_price", round(col("final_amount") / col("quantity"), 2))
        .withColumn("has_discount", when(col("discount_amount") > 0, True).otherwise(False))
        .withColumn("ingestion_timestamp", current_timestamp())
    )

# COMMAND ----------

# MAGIC %md
# MAGIC # Gold Layer - Business Analytics and Aggregations
# MAGIC
# MAGIC Create business-level metrics and aggregations for analytics

# COMMAND ----------

@dlt.table(
    name="gold_customer_lifetime_value",
    comment="Customer lifetime value metrics and segmentation",
    table_properties={
        "quality": "gold",
        "pipelines.autoOptimize.zOrderCols": "customer_id",
    },
)
def gold_customer_lifetime_value():
    """Calculate customer lifetime value and purchase behavior."""
    orders = dlt.read("silver_orders")
    customers = dlt.read("silver_customers")

    customer_metrics = (
        orders.groupBy("customer_id")
        .agg(
            count("order_id").alias("total_orders"),
            sum("total_amount").alias("lifetime_value"),
            round(sum("total_amount") / count("order_id"), 2).alias("avg_order_value"),
            min("order_ts").alias("first_order_date"),
            max("order_ts").alias("last_order_date"),
            sum(when(col("order_status") == "returned", 1).otherwise(0)).alias("returned_orders"),
            sum(when(col("order_status") == "cancelled", 1).otherwise(0)).alias("cancelled_orders"),
        )
        .withColumn(
            "customer_tenure_days",
            datediff(col("last_order_date"), col("first_order_date")),
        )
        .withColumn(
            "customer_segment",
            when(col("lifetime_value") > 5000, "VIP")
            .when(col("lifetime_value") > 1000, "High Value")
            .when(col("lifetime_value") > 500, "Medium Value")
            .otherwise("Low Value"),
        )
    )

    return customers.join(customer_metrics, "customer_id", "left").withColumn(
        "calculation_timestamp", current_timestamp()
    )


@dlt.table(
    name="gold_product_performance",
    comment="Product sales performance and inventory metrics",
    table_properties={
        "quality": "gold",
        "pipelines.autoOptimize.zOrderCols": "product_id,category",
    },
)
def gold_product_performance():
    """Calculate product performance metrics."""
    products = dlt.read("silver_products")
    order_items = dlt.read("silver_order_items")
    orders = dlt.read("silver_orders")

    # Join order items with orders to get completed orders only
    completed_items = order_items.join(
        orders.filter(col("order_status").isin(["shipped", "delivered"])), "order_id", "inner"
    )

    product_metrics = (
        completed_items.groupBy("product_id")
        .agg(
            sum("quantity").alias("total_units_sold"),
            sum("final_amount").alias("total_revenue"),
            count("order_item_id").alias("total_transactions"),
            round(sum("final_amount") / sum("quantity"), 2).alias("avg_selling_price"),
            sum("discount_amount").alias("total_discounts_given"),
        )
        .withColumn(
            "avg_discount_pct",
            round((col("total_discounts_given") / (col("total_revenue") + col("total_discounts_given"))) * 100, 2),
        )
    )

    return products.join(product_metrics, "product_id", "left").withColumn(
        "calculation_timestamp", current_timestamp()
    )


@dlt.table(
    name="gold_daily_sales_summary",
    comment="Daily sales summary with key business metrics",
    table_properties={
        "quality": "gold",
        "pipelines.autoOptimize.zOrderCols": "order_date",
    },
)
def gold_daily_sales_summary():
    """Aggregate daily sales metrics for business reporting."""
    orders = dlt.read("silver_orders")

    return (
        orders.groupBy("order_date", "order_year", "order_month", "order_quarter")
        .agg(
            count("order_id").alias("total_orders"),
            count(when(col("order_status") == "delivered", 1)).alias("delivered_orders"),
            count(when(col("order_status") == "cancelled", 1)).alias("cancelled_orders"),
            sum("total_amount").alias("total_revenue"),
            sum("subtotal").alias("total_subtotal"),
            sum("tax_amount").alias("total_tax"),
            sum("shipping_cost").alias("total_shipping"),
            round(sum("total_amount") / count("order_id"), 2).alias("avg_order_value"),
            count(col("customer_id").distinct()).alias("unique_customers"),
        )
        .withColumn(
            "cancellation_rate",
            round((col("cancelled_orders") / col("total_orders")) * 100, 2),
        )
        .withColumn("calculation_timestamp", current_timestamp())
        .orderBy("order_date")
    )


@dlt.table(
    name="gold_category_performance",
    comment="Product category performance metrics",
    table_properties={
        "quality": "gold",
        "pipelines.autoOptimize.zOrderCols": "category",
    },
)
def gold_category_performance():
    """Analyze performance by product category."""
    product_perf = dlt.read("gold_product_performance")

    return (
        product_perf.groupBy("category")
        .agg(
            count("product_id").alias("total_products"),
            sum("total_units_sold").alias("total_units_sold"),
            sum("total_revenue").alias("total_revenue"),
            round(sum("total_revenue") / count("product_id"), 2).alias("avg_revenue_per_product"),
            sum("stock_quantity").alias("total_stock_quantity"),
            count(when(col("stock_status") == "out_of_stock", 1)).alias("out_of_stock_products"),
        )
        .withColumn(
            "stock_availability_pct",
            round(
                ((col("total_products") - col("out_of_stock_products")) / col("total_products")) * 100,
                2,
            ),
        )
        .withColumn("calculation_timestamp", current_timestamp())
        .orderBy(col("total_revenue").desc())
    )
