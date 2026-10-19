from pathlib import Path
import os
import pandas as pd
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
host=os.getenv("MYSQL_HOST","localhost"); port=os.getenv("MYSQL_PORT","3306")
user=os.getenv("MYSQL_USER","root"); password=os.getenv("MYSQL_PASSWORD","")
database=os.getenv("MYSQL_DATABASE","voyage_analytics")
engine=create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}", pool_pre_ping=True)

def date_column(s):
    return pd.to_datetime(s, errors="coerce").dt.strftime("%Y-%m-%d")

# The schema is created by sql/schema.sql before running this script.
flights=pd.read_csv(DATA/"flights.csv")
flights=flights.rename(columns={"from":"from_location","to":"to_location","flightType":"flight_type","time":"travel_time","date":"travel_date"})
flights["travel_date"]=date_column(flights["travel_date"])
flights=flights[["travelCode","userCode","from_location","to_location","flight_type","price","travel_time","distance","agency","travel_date"]]
flights.columns=["travel_code","user_code","from_location","to_location","flight_type","price","travel_time","distance","agency","travel_date"]

hotels=pd.read_csv(DATA/"hotels.csv")
hotels=hotels.rename(columns={"name":"hotel_name","date":"travel_date"})
hotels["travel_date"]=date_column(hotels["travel_date"])
hotels=hotels[["travelCode","userCode","hotel_name","place","days","price","total","travel_date"]]
hotels.columns=["travel_code","user_code","hotel_name","place","days","price","total","travel_date"]

users_file=DATA/"users.csv"
if not users_file.exists():
    candidates=list(DATA.glob("users*.csv"))
    if not candidates: raise FileNotFoundError("Place users CSV in data/ and name it users.csv.")
    users_file=candidates[0]
users=pd.read_csv(users_file).rename(columns={"code":"user_code"})
users=users[["user_code","company","name","gender","age"]]

with engine.begin() as conn:
    # Reload cleanly for repeatable imports; history tables are preserved.
    conn.execute(text("DELETE FROM flights"))
    conn.execute(text("DELETE FROM hotels"))
    conn.execute(text("DELETE FROM users"))
    users.to_sql("users", conn, if_exists="append", index=False, chunksize=1000, method="multi")
    flights.to_sql("flights", conn, if_exists="append", index=False, chunksize=5000, method="multi")
    hotels.to_sql("hotels", conn, if_exists="append", index=False, chunksize=5000, method="multi")
print(f"Imported users={len(users):,}, flights={len(flights):,}, hotels={len(hotels):,}")
