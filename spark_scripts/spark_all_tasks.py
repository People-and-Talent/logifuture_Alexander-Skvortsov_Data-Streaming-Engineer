
from functools import partial
from settings import *
from pandas_udfs import *
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.streaming.state import GroupStateTimeout
from schema_models import *
import os
from pandas import DataFrame


def upsert_to_cassandra(df:DataFrame, epoch_id, table_name: str):
    df.write \
        .format("org.apache.spark.sql.cassandra") \
        .mode("append") \
        .options(table=table_name, keyspace=DB_KEY_SPACE) \
        .option("checkpointLocation", CHECK_POINT_LOC_CASSANDRA) \
        .save()


# Ensure checkpoint directory exists
# if not os.path.exists(CHECK_POINT_LOC_CASSANDRA):
#     os.makedirs(CHECK_POINT_LOC_CASSANDRA)

spark = SparkSession.builder \
    .appName("Streaming_Pipeline") \
    .config("spark.cassandra.connection.host", 'cassandra') \
    .config("spark.cassandra.connection.port", CASSANDRA_PORT) \
    .config("spark.cassandra.auth.username", CASSANDRA_USERNAME) \
    .config("spark.cassandra.auth.password", CASSANDRA_PASSWORD) \
    .config("spark.sql.streaming.checkpointLocation",CHECK_POINT_LOC_CASSANDRA) \
    .config("spark.sql.shuffle.partitions", "1") \
    .config("spark.default.parallelism", "1") \
    .config("spark.streaming.backpressure.enabled", "true") \
    .config("spark.streaming.backpressure.initialRate", "2000") \
    .config("spark.sql.streaming.stateStore.providerClass", "org.apache.spark.sql.execution.streaming.state.RocksDBStateStoreProvider") \
    .getOrCreate()



# Read messages from Kafka
messages = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", f"{KAFKA_HOST}:{KAFKA_PORT}") \
    .option("subscribe", KAFKA_TRANSACTIONS_TOPIC) \
    .option("startingOffsets", "earliest") \
    .option("failOnDataLoss", FAIL_ON_DATALOSS) \
    .option("maxOffsetsPerTrigger", MAX_OFFSET_PER_TRIGGER) \
    .load() \
    .select(from_json(col("value").cast("string"), transaction_schema).alias("data"))\
    .filter(col("data").isNotNull())\
    .select("data.*")

# Filter out messages with null values in mandatory fields
messages = messages.filter(
    col("transaction_id").isNotNull() &
    col("wallet_id").isNotNull() &
    col("product_id").isNotNull() &
    col("type").isNotNull() &
    col("amount").isNotNull() &
    col("currency").isNotNull() &
    col("timestamp").isNotNull()
)

# Question 1: Compute Balances
# Apply stateful processing to calculate the new balance for each wallet id.
balance_updates = messages.groupBy(messages["wallet_id"]).applyInPandasWithState(
    func=update_balance,
    outputMode="append",
    outputStructType=balance_output_schema,
    stateStructType="total_balance float",
    timeoutConf=GroupStateTimeout.ProcessingTimeTimeout
)

# Partial function to include table name for foreachBatch
upsert_balances_table = partial(upsert_to_cassandra, table_name="balances")

# write to cassandra table: top_credits in micro batches
balance_updates\
    .writeStream\
    .foreachBatch(upsert_balances_table)\
    .trigger(processingTime="5 seconds") \
    .start()




# Question 2: Compute Avg Debits
# Apply stateful processing using flatMapGroupsWithState
avg_debits = messages.groupBy(messages["wallet_id"]).applyInPandasWithState(
    func=update_avg_debit,
    outputMode="append",
    outputStructType=output_state_schema,
    stateStructType=state_schema,
    timeoutConf=GroupStateTimeout.ProcessingTimeTimeout
)

# Partial function to include table name for foreachBatch
upsert_avg_debits = partial(upsert_to_cassandra, table_name="avg_debits")

# write to cassandra table: top_credits in micro batches
avg_debits\
    .writeStream\
    .foreachBatch(upsert_avg_debits)\
    .trigger(processingTime="5 seconds") \
    .start()



# Question 3: Top 5 Credits
# Apply stateful processing using applyInPandasWithState
# This operation is for calculating the top 5 credits of each product id
top_5_credits_df = messages.groupBy(messages["product_id"]).applyInPandasWithState(
    func=update_top5_credits,
    outputMode="append",
    outputStructType=output_top5_credits_schema,
    stateStructType=state_schema_top5_credits,
    timeoutConf=GroupStateTimeout.ProcessingTimeTimeout
)


# Partial function to include table name for foreachBatch
upsert_top5_credits = partial(upsert_to_cassandra, table_name="top_credits")

# write to cassandra table: top_credits in micro batches
top_5_credits_df\
    .writeStream\
    .foreachBatch(upsert_top5_credits)\
    .trigger(processingTime="5 seconds") \
    .start()


# required to keep spark streaming
spark.streams.awaitAnyTermination()
