from pyspark.sql.types import StructType, StructField, StringType, DecimalType, TimestampType, LongType, FloatType, \
    IntegerType

# Define Kafka message schema
transaction_schema = StructType([
    StructField("transaction_id", StringType(), False),
    StructField("wallet_id", StringType(), False),
    StructField("product_id", StringType(), False),
    StructField("type", StringType(), False),
    StructField("amount", FloatType(), False),
    StructField("currency", StringType(), False),
    StructField("timestamp", TimestampType(), False)
])






########## Question 1: Balances ################
# Define state schema for Pandas UDF.
# It is used by update_balance() when returning the newily calculated balance for each wallet in real time
balance_output_schema = StructType([
    StructField("wallet_id", StringType()),
    StructField("currency", StringType()),
    StructField("balance", FloatType())
])

################################################




########## Question 2: Avg debits ################

# Define state schema for Pandas UDF
output_state_schema = StructType([
    StructField("wallet_id", StringType()),
    StructField("avg_debit", FloatType())
])


# Define state schema for Pandas UDF
state_schema = StructType([
    StructField("total_debit", FloatType()),
    StructField("debit_days", IntegerType()),
    StructField("last_transaction_date", TimestampType())
])

##############################

########## Question 3: Top 5 Credits ################
# Define the state schema for top 5 credits
output_top5_credits_schema = StructType([
    StructField("product_id", StringType()),
    StructField("top_5_credits", StringType()),
])

state_schema_top5_credits = StructType([StructField("top_5credits", StringType())])