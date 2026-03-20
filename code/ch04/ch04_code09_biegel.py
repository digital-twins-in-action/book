from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, date_trunc, sum as spark_sum, col
from pyspark.sql.types import *

# Create Spark session
spark = SparkSession.builder.appName("WeeklyUsage").getOrCreate()

# Read CSV file with proper schema
schema = StructType([
    StructField("datetime_utc", TimestampType(), True),
    StructField("datetime_local", TimestampType(), True),
    StructField("watt_hours", DoubleType(), True),
    StructField("cost_dollars", DoubleType(), True),
    StructField("is_peak", BooleanType(), True)
])

df = spark.read.option("header", "true").schema(schema).csv("powerpal_data.csv")

# Calculate weekly usage using datetime_local
weekly_usage = df.groupBy(
    date_trunc("week", col("datetime_local")).alias("week_start")
).agg(
    spark_sum("watt_hours").alias("total_watt_hours")
).orderBy("week_start")

# Show results
print("Weekly Usage:")
weekly_usage.show()

print("\nSummary:")
weekly_usage.agg(
    spark_sum("total_watt_hours").alias("total_usage"),
    avg("total_watt_hours").alias("avg_weekly_usage")
).show()

# Stop Spark session
spark.stop()
