import psycopg2
from sqlalchemy import create_engine
import os
import pandas as pd
import logging

# Setup logs
logging.basicConfig(filename='errors.log', level=logging.ERROR)

# Functions for PostgreSQL
def connect_postgresql():
    # Testing connection and engine
    conn = psycopg2.connect(database="mmsi",
                            host="localhost",
                            user="postgres",
                            password=os.environ.get("PG_PASSWORD"),
                            port=5432)


    ## engine to write to postgres from dataframe
    engine= create_engine(f'postgresql://postgres:{os.environ.get("PG_PASSWORD")}@localhost:5432/mmsi')

    return conn, engine


def create_table(query, conn):
    try:

        cur = conn.cursor()
        cur.execute(query)
        conn.commit()  # Commit changes
        print("Created table successfully")
    except Exception as e:
        logging.error(f"An error occurred with the batch insert: {e}")

def insert_values(df, table_name, engine):
    try:
        df.to_sql(table_name, engine, if_exists='append', index=False, method='multi')
        print("successfully inserted values")
    except Exception as e:
        logging.error(f"An error occurred with the batch insert: {e}")

def close_postgresql_connection(conn):
    conn.close()

# Queries to create tables
query_dim_date = '''
CREATE TABLE IF NOT EXISTS dim_date (
    date_id VARCHAR PRIMARY KEY,
    date DATE,
    day SMALLINT,
    month SMALLINT,
    year SMALLINT,
    day_of_week SMALLINT,
    weekend SMALLINT
);
'''

query_dim_time = '''
CREATE TABLE IF NOT EXISTS dim_time (
    time_id VARCHAR PRIMARY KEY,
    time TIME,
    hour SMALLINT,
    minute SMALLINT,
    second SMALLINT,
    is_noon SMALLINT,
    is_midnight SMALLINT,
    am_pm VARCHAR
);
'''

query_dim_location = '''
CREATE TABLE IF NOT EXISTS dim_location (
    location_id VARCHAR PRIMARY KEY,
    lon FLOAT,
    lat FLOAT,
    grid VARCHAR,
    port VARCHAR
);
'''

query_dim_vessel_type = '''
CREATE TABLE IF NOT EXISTS dim_vessel (
    vessel_id VARCHAR PRIMARY KEY,
    mmsi INTEGER,
    imo VARCHAR,
    callsign VARCHAR,
    shipname VARCHAR,
    shiptype INTEGER,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    is_current SMALLINT
);
'''

query_fact_messsage_type_1 = '''
CREATE TABLE IF NOT EXISTS fact_messages_type_1 (
    message_type_1_id VARCHAR PRIMARY KEY,
    location_id VARCHAR,
    date_id VARCHAR,
    time_id VARCHAR,
    vessel_id VARCHAR,
    status FLOAT,
    turn FLOAT,
    accuracy FLOAT,
    CONSTRAINT fk_location_id
        FOREIGN KEY (location_id)
        REFERENCES dim_location (location_id),
    CONSTRAINT fk_date_id
        FOREIGN KEY (date_id)
        REFERENCES dim_date (date_id),
    CONSTRAINT fk_time_id
        FOREIGN KEY (time_id)
        REFERENCES dim_time (time_id),
    CONSTRAINT fk_vessel_id
        FOREIGN KEY (vessel_id)
        REFERENCES dim_vessel (vessel_id)
);
'''

query_fact_messsage_type_5 = '''
CREATE TABLE IF NOT EXISTS fact_messages_type_5 (
    message_type_5_id VARCHAR PRIMARY KEY,
    date_id VARCHAR,
    time_id VARCHAR,
    vessel_id VARCHAR,
    to_bow FLOAT,
    to_stern FLOAT,
    to_port FLOAT,
    to_starboard FLOAT,
    eta_month FLOAT,
    eta_day FLOAT,
    eta_hour FLOAT,
    eta_minute FLOAT,
    eta_draught FLOAT,
    eta_destination VARCHAR,
    CONSTRAINT fk_date_id2
        FOREIGN KEY (date_id)
        REFERENCES dim_date (date_id),
    CONSTRAINT fk_time_id2
        FOREIGN KEY (time_id)
        REFERENCES dim_time (time_id),
    CONSTRAINT fk_vessel_id2
        FOREIGN KEY (vessel_id)
        REFERENCES dim_vessel (vessel_id)
);
'''



# Main Driver Function
def main():
    # Load all cleaned datasets
    dim_location = pd.read_csv("dim_location_gridNauticalMile.csv")
    dim_location = dim_location.drop(columns=['Unnamed: 0'])
    dim_location["grid"] = dim_location["grid"].astype(str)

    dim_vessel = pd.read_csv("dim_vessel_type_final.csv")
    dim_vessel = dim_vessel.drop(columns=['Unnamed: 0'])
    dim_vessel["is_current"] = dim_vessel["is_current"].astype(int)
    dim_vessel["shiptype"] = dim_vessel["shiptype"].astype(int)

    dim_time = pd.read_csv("dim_time.csv")
    dim_time = dim_time.drop(columns=['Unnamed: 0'])

    dim_date = pd.read_csv("dim_date.csv")
    dim_date = dim_date.drop(columns=['Unnamed: 0'])

    fact_messages_type_1 = pd.read_csv("fact_messages_type_1.csv")
    fact_messages_type_1 = fact_messages_type_1.drop(columns=['Unnamed: 0'])

    fact_messages_type_5 = pd.read_csv("fact_messages_type_5.csv")
    fact_messages_type_5 = fact_messages_type_5.drop(columns=['Unnamed: 0'])

    # Setup PostgreSQL connection
    conn, engine = connect_postgresql()

    # Table Creation and Insertion for all facts and dimensions
    create_table(query_dim_date, conn)
    insert_values(dim_date, "dim_date", engine)
    create_table(query_dim_time, conn)
    insert_values(dim_time, "dim_time", engine)
    create_table(query_dim_location, conn)
    insert_values(dim_location, "dim_location", engine)
    create_table(query_dim_vessel_type, conn)
    insert_values(dim_vessel, "dim_vessel", engine)
    create_table(query_fact_messsage_type_1, conn)
    insert_values(fact_messages_type_1, "fact_messages_type_1", engine)
    create_table(query_fact_messsage_type_5, conn)
    insert_values(fact_messages_type_5, "fact_messages_type_5", engine)
    close_postgresql_connection(conn)



if __name__ == '__main__':
    main()