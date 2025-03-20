from neo4j import GraphDatabase
import pandas as pd
import os
import logging
import sqlite3
import math


# MATCH (n)
# WITH n LIMIT 1000
# DETACH DELETE n;

# SHOW CONSTRAINTS;

# SHOW INDEXES;
# DROP INDEX index_f7700477;

# MATCH (n:Stock)
# RETURN count(n) AS stock;

# Count Description Nodes with Embedding
# MATCH (n:Description)
# WHERE n.embedding IS NOT NULL
# RETURN count(n) AS node_count

# Remove embedding property from Description Nodes
# MATCH (n:Description)
# REMOVE n.embedding

NEO4J_URI = os.getenv("NEO4J_URI")
print(NEO4J_URI)
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(NEO4J_URI, 
                              auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
                              max_connection_lifetime=1000, 
                              connection_timeout=30,
                              max_connection_pool_size=50 )


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

LOGGER = logging.getLogger(__name__)



def create_indexes():
    """Create necessary indexes in Neo4j."""
    indexes = [
        "CREATE INDEX IF NOT EXISTS FOR (s:Stock) ON (s.symbol);",
        "CREATE INDEX IF NOT EXISTS FOR (c:Country) ON (c.name);",
        "CREATE INDEX IF NOT EXISTS FOR (s:Sector) ON (s.name);",
        "CREATE INDEX IF NOT EXISTS FOR (i:Industry) ON (i.name);",
        "CREATE INDEX IF NOT EXISTS FOR (a:Attribute) ON (a.type, a.value);",
        "CREATE INDEX IF NOT EXISTS FOR (d:Description) ON (d.text);",
        "CREATE INDEX IF NOT EXISTS FOR (d:Description_Chunk) ON (d.text);"
    ]
    
    with driver.session() as session:
        for index_query in indexes:
            session.execute_write(lambda tx: tx.run(index_query))
            LOGGER.info(f"Index created: {index_query.strip()}")
    LOGGER.info("All indexes created successfully.")

def write_batch_to_neo4j(tx, batch):
    """Write a batch of rows into Neo4j with optimized Cypher."""
    tx.run("""
    UNWIND $rows AS row

    // Create Stock node and attributes
    MERGE (stock:Stock {symbol: row.symbol})
    SET stock.name = row.name,
        stock.exchange = row.stock_exchange,
        stock.data_points = row.data_points,
        stock.yearly_return = row.return_coeff,
        stock.yearly_volatility = row.volatility_coeff,
        stock.market_capitalization_amount = row.market_cap_euro,
        stock.average_trading_volume_amount = row.avg_trade_vol_euro,
        stock.beta = row.beta

    // Create Country node
    MERGE (country:Country {name: row.country})
    ON CREATE SET country.country_full_name = row.country_full_name
    ON MATCH SET country.country_full_name = row.country_full_name
    MERGE (stock)-[:BASED_IN]->(country)

    // Create Sector and Industry nodes
    MERGE (sector:Sector {name: row.sector})
    MERGE (stock)-[:BELONGS_TO_SECTOR]->(sector)
           
    MERGE (industry:Industry {name: row.industry})
    MERGE (stock)-[:BELONGS_TO_INDUSTRY]->(industry)
           
    // Create Description node
    MERGE (desc:Description {text: row.description})
    SET desc.symbol = row.symbol,
        desc.name = row.name,
        desc.exchange = row.exchange
    MERGE (stock)-[:HAS_DESCRIPTION]->(desc)

    // Create one Attribute node for the Stock
    MERGE (attribute:Attribute {symbol: row.symbol})
    SET attribute.market_capitalization = row.market_capitalization,
        attribute.volatility = row.volatility,
        attribute.return = row.return,
        attribute.average_trading_volume = row.average_trading_volume
    MERGE (stock)-[:HAS_ATTRIBUTE]->(attribute)

    // Handle Description Chunks
    // WITH stock, row
    // UNWIND row.description_chunks AS chunk
    // MERGE (desc_chunk:Description_Chunk {text: chunk})
    // MERGE (stock)-[:HAS_DESCRIPTION_CHUNK]->(desc_chunk)
    """, rows=batch)



    #CREATE (desc:Description {text: row.description})
    #CREATE (stock)-[:HAS_DESCRIPTION]->(desc);


def load_data_in_batches(df, batch_size):
    """Load data into Neo4j in batches."""
    total_rows = len(df)
    num_batches = math.ceil(total_rows / batch_size)
    
    LOGGER.info(f"Loading {total_rows} rows into Neo4j in {num_batches} batches...")
    
    with driver.session() as session:
        for i in range(0, total_rows, batch_size):
            batch = df.iloc[i:i + batch_size].to_dict(orient="records")
            session.execute_write(write_batch_to_neo4j, batch)
            LOGGER.info(f"Batch {i // batch_size + 1}/{num_batches} loaded.")

    LOGGER.info("Data successfully written to Neo4j!")


