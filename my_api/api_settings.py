from os import getenv

from pathlib import Path

PROJECT_PATH = Path(__file__).resolve().parent



# db_scripts settings

DB_KEY_SPACE = getenv('DB_KEY_SPACE', 'betting')
CASSANDRA_USERNAME = getenv('CASSANDRA_USERNAME', 'cassandra')
CASSANDRA_PASSWORD = getenv('CASSANDRA_PASSWORD', 'cassandra')
CASSANDRA_PORT = getenv('CASSANDRA_PORT', '9042')

DB_CONN_ATTEMPTS = getenv('DB_CONN_ATTEMPTS', 30)
DB_CONN_RETRY_DELAY = getenv('DB_CONN_RETRY_DELAY', 10)
