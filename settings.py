from os import getenv

from pathlib import Path

PROJECT_PATH = Path(__file__).resolve().parent


CHECK_POINT_LOC_CASSANDRA = getenv('CHECK_POINT_LOC_CASSANDRA',PROJECT_PATH / 'tmp/cassandra_checkpoint')



# db_scripts settings

DB_KEY_SPACE = getenv('DB_KEY_SPACE', 'betting')
CASSANDRA_USERNAME = getenv('CASSANDRA_USERNAME', 'cassandra')
CASSANDRA_PASSWORD = getenv('CASSANDRA_PASSWORD', 'cassandra')
CASSANDRA_PORT = getenv('CASSANDRA_PORT', '9042')

DB_CONN_ATTEMPTS = getenv('DB_CONN_ATTEMPTS', 30)
DB_CONN_RETRY_DELAY = getenv('DB_CONN_RETRY_DELAY', 10)


# Kafka settings

KAFKA_HOST = getenv('KAFKA_HOST','localhost')
KAFKA_PORT = getenv('KAFKA_PORT','29092')
KAFKA_TRANSACTIONS_TOPIC = getenv('KAFKA_TRANSACTIONS_TOPIC','transactions_topic')
FAIL_ON_DATALOSS = getenv('FAIL_ON_DATALOSS', 'false')
MAX_OFFSET_PER_TRIGGER = getenv('MAX_OFFSET_PER_TRIGGER', '1000')


# Spark settings

SPARK_HOST = getenv('SPARK_HOST','localhost')