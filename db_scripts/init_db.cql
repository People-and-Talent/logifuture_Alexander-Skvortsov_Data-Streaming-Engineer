CREATE KEYSPACE IF NOT EXISTS betting WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': '1'
};

USE betting;

CREATE TABLE IF NOT EXISTS avg_debits (
    wallet_id text PRIMARY KEY,
    avg_debit float,
    updated_at date
);

CREATE TABLE IF NOT EXISTS top_credits (
    product_id text PRIMARY KEY,
    top_5_credits text
);


CREATE TABLE IF NOT EXISTS balances (
    wallet_id text PRIMARY KEY,
    balance float,
    currency text
);
