import sqlite3
import logging
from datetime import datetime
import os
from dotenv import load_dotenv


db_file = "../stocks_data.db"
conn = sqlite3.connect(db_file)
cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS hist_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    date TEXT NOT NULL,
    close REAL NOT NULL,
    volume INTEGER NOT NULL,
    UNIQUE(symbol, date) ON CONFLICT IGNORE
);
""")
conn.commit()


cursor.execute("""
CREATE TABLE IF NOT EXISTS hist_mcaps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    date TEXT NOT NULL,
    mcap REAL NOT NULL,
    UNIQUE(symbol, date) ON CONFLICT IGNORE
);
""")
conn.commit()


cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS stock_info (
        symbol TEXT PRIMARY KEY,
        name TEXT,
        country TEXT,
        currency TEXT,
        stock_exchange TEXT,
        exchange_short_name TEXT,
        industry TEXT,
        sector TEXT,
        beta REAL,
        price REAL,
        avg_vol REAL,       
        market_cap REAL,
        description TEXT
    )
    """)
conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS exchange_rates (
    date TEXT PRIMARY KEY
)
""")
conn.commit()


###########################################################

def insert_hist_prices(records, conn):

    cursor = conn.cursor()

    insert_query = """
    INSERT INTO hist_prices (symbol, date, close, volume)
    VALUES (:symbol, :date, :close, :volume)
    """
    cursor.executemany(insert_query, records)
    conn.commit()



def insert_hist_mcaps(records, conn):

    cursor = conn.cursor()

    insert_query = """
    INSERT INTO hist_mcaps (symbol, date, mcap)
    VALUES (:symbol, :date, :marketCap)
    """
    cursor.executemany(insert_query, records)
    conn.commit()


def write_ccy_data(cursor, ccy_pair, stock_data, table_name):
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN '{ccy_pair}' REAL")

        for record in stock_data:
            date = record['date']
            close = record['close']

            cursor.execute(f"SELECT 1 FROM {table_name} WHERE date = ?", (date,))
            if cursor.fetchone():
                cursor.execute(f"UPDATE {table_name} SET '{ccy_pair}' = ? WHERE date = ?", (close, date))
            else:
                cursor.execute(f"INSERT INTO {table_name} (date, '{ccy_pair}') VALUES (?, ?)", (date, close))
            conn.commit()



def write_stock_data(data, table_name):
    if not data:
        logging.info("No data to write to SQLite.")
        return

    try:
        with sqlite3.connect("stocks_data.db") as conn:
            cursor = conn.cursor()

            # Insert data
            try:
                cursor.executemany(f"""
                INSERT INTO "{table_name}" (symbol, name, country, currency, stock_exchange, exchange_short_name, industry, sector, beta, 'price', 'avg_vol', market_cap, description)
                VALUES (:symbol, :companyName, :country, :currency, :exchange, :exchangeShortName, :industry, :sector, :beta, :price, :volAvg , :mktCap, :description)
                """, data)
            except sqlite3.IntegrityError as e:
                logging.error(f"Skipping duplicate record: {e}")

            conn.commit()
            logging.info(f"Data successfully written to table: {table_name}")

    except sqlite3.Error as e:
        logging.error(f"SQLite error: {e}")

