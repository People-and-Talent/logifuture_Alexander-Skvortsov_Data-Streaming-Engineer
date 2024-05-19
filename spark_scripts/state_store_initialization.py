import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, struct
from pyspark.sql.streaming.state import GroupState, GroupStateTimeout
from pyspark.sql.types import StructType, StructField, StringType, DecimalType, FloatType


def initialize_spark_session():
    return SparkSession.builder \
        .appName("StateInitialization") \
        .config("spark.sql.streaming.checkpointLocation", "/tmp/spark-checkpoints") \
        .config("spark.sql.streaming.stateStore.providerClass", "org.apache.spark.sql.execution.streaming.state.RocksDBStateStoreProvider") \
        .config("spark.cassandra.connection.host", "cassandra") \
        .config("spark.cassandra.auth.username", "cassandra") \
        .config("spark.cassandra.auth.password", "cassandra") \
        .getOrCreate()

def load_initial_balances(spark):
    return spark.read \
        .format("org.apache.spark.sql.cassandra") \
        .options(table="balances", keyspace="betting") \
        .load()

# def initialize_state_from_db(wallet_id, balances, state: GroupState):
#     if state.exists:
#         return state.get
#     balance = balances.collect()[0]["balance"]
#     state.update(balance)
#     return balance

def initialize_state_from_db(pdf):
    # Initialize the state from the database
    pdf['state'] = pdf['balance']
    return pdf[['wallet_id', 'state']]

def populate_state_store(spark, checkpoint_dir):
    initial_balances_df = load_initial_balances(spark)
    # initial_state_rdd = initial_balances_df.select("wallet_id", "balance") \
    #     .rdd.map(lambda row: (row["wallet_id"], row["balance"]))
    #
    # initial_state_df = initial_state_rdd.toDF(["wallet_id", "balance"])
    state_schema = StructType([
        StructField("wallet_id", StringType(), True),
        StructField("balance", FloatType(), True),
        StructField("state", FloatType(), True)
    ])

    stateful_initialization = initial_balances_df.groupBy("wallet_id").applyInPandas(
        func=initialize_state_from_db,
        # outputMode="append",
        # outputStructType='bal float',
        schema=state_schema,
        # timeoutConf=GroupStateTimeout.NoTimeout
    )
    # stateful_initialization.show()


    # Write the initial state to a temporary location to make sure it's applied
    stateful_initialization.write.mode("overwrite").format("noop").save()

    # Write the initial state to a temporary location to make sure it's applied
    # temp_location = "/tmp/initial_state"
    # initial_state_df.write.mode("overwrite").parquet(temp_location)

def main():
    spark = initialize_spark_session()
    checkpoint_dir = spark.conf.get("spark.sql.streaming.checkpointLocation")

    # Check if the checkpoint directory exists
    if not any(os.path.exists(checkpoint_dir) for checkpoint_dir in checkpoint_dir.split(",")):
        populate_state_store(spark, checkpoint_dir)

if __name__ == "__main__":
    main()
