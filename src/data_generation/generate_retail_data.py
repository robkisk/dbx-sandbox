# Databricks notebook source
"""Generate synthetic retail/e-commerce data using dbldatagen.

This module creates realistic synthetic data for an e-commerce platform including:
- Customers
- Products
- Orders
- Order line items

The generated data can be used for testing Delta Live Tables pipelines,
benchmarking, and development purposes.
"""

# COMMAND ----------

from pyspark.sql import SparkSession
from pyspark.sql.types import (
    DecimalType,
    IntegerType,
    LongType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

import dbldatagen as dg

# COMMAND ----------

def generate_customer_data(
    spark: SparkSession,
    num_customers: int = 100000,
    partitions: int = 8,
    output_path: str | None = None,
) -> None:
    """Generate synthetic customer data.

    Args:
        spark: Active SparkSession
        num_customers: Number of unique customers to generate
        partitions: Number of partitions for the output
        output_path: Optional path to write the data (Delta format)
    """
    # Countries and their relative weights (population-based)
    countries = ["US", "UK", "CA", "AU", "DE", "FR", "JP", "IN", "BR", "MX"]
    country_weights = [330, 67, 38, 26, 83, 67, 126, 1400, 214, 130]

    customer_spec = (
        dg.DataGenerator(
            spark,
            name="customer_data",
            rows=num_customers,
            partitions=partitions,
            randomSeedMethod="hash_fieldname",
        )
        .withIdOutput()
        .withColumn(
            "customer_id",
            LongType(),
            minValue=1000000,
            maxValue=1000000 + num_customers,
            uniqueValues=num_customers,
        )
        .withColumn(
            "first_name",
            StringType(),
            template=r"\w \w|\w\w|\w\w\w",
            random=True,
        )
        .withColumn(
            "last_name",
            StringType(),
            template=r"\w\w\w\w|\w\w\w\w\w|\w\w\w\w\w\w",
            random=True,
        )
        .withColumn(
            "email",
            StringType(),
            expr="lower(concat(first_name, '.', last_name, '@', 'example.com'))",
            baseColumn=["first_name", "last_name"],
        )
        .withColumn(
            "country",
            StringType(),
            values=countries,
            weights=country_weights,
            baseColumn="customer_id",
        )
        .withColumn(
            "account_created_ts",
            TimestampType(),
            begin="2020-01-01 00:00:00",
            end="2024-12-31 23:59:59",
            interval="1 hour",
            random=True,
        )
        .withColumn(
            "loyalty_tier",
            StringType(),
            values=["bronze", "silver", "gold", "platinum"],
            weights=[50, 30, 15, 5],
            random=True,
        )
    )

    df_customers = customer_spec.build()

    if output_path:
        df_customers.write.format("delta").mode("overwrite").save(output_path)
        print(f"✓ Customer data written to {output_path}")
    else:
        df_customers.show(10)

    return df_customers

# COMMAND ----------

def generate_product_data(
    spark: SparkSession,
    num_products: int = 10000,
    partitions: int = 4,
    output_path: str | None = None,
) -> None:
    """Generate synthetic product catalog data.

    Args:
        spark: Active SparkSession
        num_products: Number of unique products to generate
        partitions: Number of partitions for the output
        output_path: Optional path to write the data (Delta format)
    """
    categories = [
        "Electronics",
        "Clothing",
        "Home & Garden",
        "Sports",
        "Books",
        "Toys",
        "Beauty",
        "Automotive",
    ]
    brands = [
        "BrandA",
        "BrandB",
        "BrandC",
        "BrandD",
        "BrandE",
        "Generic",
    ]

    product_spec = (
        dg.DataGenerator(
            spark,
            name="product_data",
            rows=num_products,
            partitions=partitions,
            randomSeedMethod="hash_fieldname",
        )
        .withIdOutput()
        .withColumn(
            "product_id",
            LongType(),
            minValue=5000000,
            maxValue=5000000 + num_products,
            uniqueValues=num_products,
        )
        .withColumn(
            "product_sku",
            StringType(),
            format="SKU-%09d",
            baseColumn="product_id",
        )
        .withColumn(
            "category",
            StringType(),
            values=categories,
            baseColumn="product_id",
            baseColumnType="hash",
        )
        .withColumn(
            "brand",
            StringType(),
            values=brands,
            random=True,
        )
        .withColumn(
            "product_name",
            StringType(),
            template=r"\w\w\w \w\w\w\w \w\w\w",
            random=True,
        )
        .withColumn(
            "unit_price",
            DecimalType(10, 2),
            minValue=5.00,
            maxValue=2000.00,
            step=0.01,
            distribution="normal",
            baseColumn="category",
            baseColumnType="hash",
        )
        .withColumn(
            "stock_quantity",
            IntegerType(),
            minValue=0,
            maxValue=1000,
            distribution="normal",
            random=True,
        )
        .withColumn(
            "is_active",
            StringType(),
            values=["Y", "N"],
            weights=[95, 5],
            random=True,
        )
    )

    df_products = product_spec.build()

    if output_path:
        df_products.write.format("delta").mode("overwrite").save(output_path)
        print(f"✓ Product data written to {output_path}")
    else:
        df_products.show(10)

    return df_products

# COMMAND ----------

def generate_order_data(
    spark: SparkSession,
    num_orders: int = 500000,
    num_customers: int = 100000,
    partitions: int = 8,
    output_path: str | None = None,
) -> None:
    """Generate synthetic order transaction data.

    Args:
        spark: Active SparkSession
        num_orders: Number of orders to generate
        num_customers: Number of unique customers (for referential integrity)
        partitions: Number of partitions for the output
        output_path: Optional path to write the data (Delta format)
    """
    order_statuses = [
        "pending",
        "processing",
        "shipped",
        "delivered",
        "cancelled",
        "returned",
    ]
    status_weights = [5, 10, 20, 55, 7, 3]

    payment_methods = ["credit_card", "debit_card", "paypal", "apple_pay", "google_pay"]

    order_spec = (
        dg.DataGenerator(
            spark,
            name="order_data",
            rows=num_orders,
            partitions=partitions,
            randomSeedMethod="hash_fieldname",
        )
        .withIdOutput()
        .withColumn(
            "order_id",
            LongType(),
            minValue=8000000,
            maxValue=8000000 + num_orders,
            uniqueValues=num_orders,
        )
        .withColumn(
            "customer_id",
            LongType(),
            minValue=1000000,
            maxValue=1000000 + num_customers,
            random=True,
        )
        .withColumn(
            "order_ts",
            TimestampType(),
            begin="2024-01-01 00:00:00",
            end="2024-12-31 23:59:59",
            interval="1 minute",
            random=True,
        )
        .withColumn(
            "order_status",
            StringType(),
            values=order_statuses,
            weights=status_weights,
            random=True,
        )
        .withColumn(
            "payment_method",
            StringType(),
            values=payment_methods,
            random=True,
        )
        .withColumn(
            "num_items",
            IntegerType(),
            minValue=1,
            maxValue=10,
            distribution="normal",
            random=True,
        )
        .withColumn(
            "subtotal",
            DecimalType(10, 2),
            minValue=10.00,
            maxValue=5000.00,
            step=0.01,
            distribution="normal",
            random=True,
        )
        .withColumn(
            "tax_amount",
            DecimalType(10, 2),
            expr="round(subtotal * 0.08, 2)",
            baseColumn="subtotal",
        )
        .withColumn(
            "shipping_cost",
            DecimalType(10, 2),
            minValue=0.00,
            maxValue=50.00,
            step=0.01,
            distribution="normal",
            random=True,
        )
        .withColumn(
            "total_amount",
            DecimalType(10, 2),
            expr="subtotal + tax_amount + shipping_cost",
            baseColumn=["subtotal", "tax_amount", "shipping_cost"],
        )
        .withColumn(
            "shipped_ts",
            TimestampType(),
            begin="2024-01-02 00:00:00",
            end="2024-12-31 23:59:59",
            interval="1 minute",
            random=True,
            percentNulls=0.2,
        )
        # Apply constraint: shipped_ts must be after order_ts
        .withSqlConstraint("shipped_ts is null or shipped_ts > order_ts")
    )

    df_orders = order_spec.build()

    if output_path:
        df_orders.write.format("delta").mode("overwrite").save(output_path)
        print(f"✓ Order data written to {output_path}")
    else:
        df_orders.show(10)

    return df_orders

# COMMAND ----------

def generate_order_items_data(
    spark: SparkSession,
    num_order_items: int = 1000000,
    num_orders: int = 500000,
    num_products: int = 10000,
    partitions: int = 8,
    output_path: str | None = None,
) -> None:
    """Generate synthetic order line items data.

    Args:
        spark: Active SparkSession
        num_order_items: Number of order line items to generate
        num_orders: Number of unique orders (for referential integrity)
        num_products: Number of unique products (for referential integrity)
        partitions: Number of partitions for the output
        output_path: Optional path to write the data (Delta format)
    """
    order_items_spec = (
        dg.DataGenerator(
            spark,
            name="order_items_data",
            rows=num_order_items,
            partitions=partitions,
            randomSeedMethod="hash_fieldname",
        )
        .withIdOutput()
        .withColumn(
            "order_item_id",
            LongType(),
            minValue=9000000,
            maxValue=9000000 + num_order_items,
            uniqueValues=num_order_items,
        )
        .withColumn(
            "order_id",
            LongType(),
            minValue=8000000,
            maxValue=8000000 + num_orders,
            random=True,
        )
        .withColumn(
            "product_id",
            LongType(),
            minValue=5000000,
            maxValue=5000000 + num_products,
            random=True,
        )
        .withColumn(
            "quantity",
            IntegerType(),
            minValue=1,
            maxValue=5,
            distribution="normal",
            random=True,
        )
        .withColumn(
            "unit_price",
            DecimalType(10, 2),
            minValue=5.00,
            maxValue=2000.00,
            step=0.01,
            distribution="normal",
            random=True,
        )
        .withColumn(
            "line_total",
            DecimalType(10, 2),
            expr="round(quantity * unit_price, 2)",
            baseColumn=["quantity", "unit_price"],
        )
        .withColumn(
            "discount_pct",
            DecimalType(5, 2),
            minValue=0.00,
            maxValue=0.50,
            step=0.01,
            random=True,
            percentNulls=0.7,
        )
        .withColumn(
            "discount_amount",
            DecimalType(10, 2),
            expr="coalesce(round(line_total * discount_pct, 2), 0.00)",
            baseColumn=["line_total", "discount_pct"],
        )
        .withColumn(
            "final_amount",
            DecimalType(10, 2),
            expr="line_total - discount_amount",
            baseColumn=["line_total", "discount_amount"],
        )
    )

    df_order_items = order_items_spec.build()

    if output_path:
        df_order_items.write.format("delta").mode("overwrite").save(output_path)
        print(f"✓ Order items data written to {output_path}")
    else:
        df_order_items.show(10)

    return df_order_items

# COMMAND ----------

def main() -> None:
    """Generate all retail datasets."""
    spark = SparkSession.builder.appName("RetailDataGenerator").getOrCreate()

    # Configuration
    base_path = "/tmp/retail_data"
    num_customers = 100000
    num_products = 10000
    num_orders = 500000
    num_order_items = 1000000

    print("=" * 60)
    print("Generating Synthetic Retail Data with dbldatagen")
    print("=" * 60)

    # Generate datasets
    print("\n1. Generating Customer Data...")
    generate_customer_data(
        spark,
        num_customers=num_customers,
        output_path=f"{base_path}/customers",
    )

    print("\n2. Generating Product Data...")
    generate_product_data(
        spark,
        num_products=num_products,
        output_path=f"{base_path}/products",
    )

    print("\n3. Generating Order Data...")
    generate_order_data(
        spark,
        num_orders=num_orders,
        num_customers=num_customers,
        output_path=f"{base_path}/orders",
    )

    print("\n4. Generating Order Items Data...")
    generate_order_items_data(
        spark,
        num_order_items=num_order_items,
        num_orders=num_orders,
        num_products=num_products,
        output_path=f"{base_path}/order_items",
    )

    print("\n" + "=" * 60)
    print("✓ All datasets generated successfully!")
    print(f"Base path: {base_path}")
    print("=" * 60)

# COMMAND ----------

if __name__ == "__main__":
    main()
