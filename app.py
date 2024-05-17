import datetime
import time
from fastapi import FastAPI
from cassandra.cluster import Cluster, PlainTextAuthProvider
from settings import *

app = FastAPI()



for attempt in range(DB_CONN_ATTEMPTS):
    try:
        auth_provider = PlainTextAuthProvider(username=CASSANDRA_USERNAME, password=CASSANDRA_PASSWORD)
        cluster = Cluster(['cassandra'], auth_provider=auth_provider)
        session = cluster.connect('betting')
        break
    except Exception as e:
        print(f"{datetime.datetime.now()}  Error connecting to Cassandra: {e}, retrying in {DB_CONN_RETRY_DELAY} seconds...")
        time.sleep(DB_CONN_RETRY_DELAY)
else:
    raise Exception("Failed to connect to Cassandra after several attempts")



@app.get("/balance/{wallet_id}")
def get_balance(wallet_id: str):
    query = "SELECT balance, currency FROM balances WHERE walletID = %s"
    row = session.execute(query, [wallet_id]).one()
    if row:
        return {"walletID": wallet_id, "balance": row.balance, "currency": row.currency}
    else:
        return {"error": "Wallet ID not found"}



@app.get("/average_daily_debit/{wallet_id}")
def get_avg_daily_debit(wallet_id: str):
    query = "SELECT avg_debit FROM avg_debits WHERE wallet_id = %s"
    row = session.execute(query, [wallet_id]).one()
    if row:
        return {"wallet_id": wallet_id, "avg_debit": row.avg_debit}
    else:
        return {"error": "Wallet ID not found"}



@app.get("/top_credits/{product_id}")
def get_top_credits(product_id: str):
    query = "SELECT top_5_credits FROM top_credits WHERE product_id = %s"
    row = session.execute(query, [product_id]).one()

    if row:
        return {"product_id": product_id, "top_5_credits": row.top_5_credits}
    else:
        return {"error": "Product ID not found"}