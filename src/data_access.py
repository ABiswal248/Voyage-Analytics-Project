import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

def mysql_engine():
    if os.getenv("USE_MYSQL", "1") == "0":
        return None
    host = os.getenv("MYSQL_HOST", "localhost")
    port = os.getenv("MYSQL_PORT", "3306")
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")
    database = os.getenv("MYSQL_DATABASE", "voyage_analytics")
    url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    try:
        engine = create_engine(url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as exc:
        print(f"[INFO] MySQL unavailable; using CSV fallback. Reason: {exc}")
        return None

def read_table(table, csv_name):
    engine = mysql_engine()
    if engine is not None:
        return pd.read_sql_table(table, engine)
    path = DATA / csv_name
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Place the supplied CSV in data/.")
    df = pd.read_csv(path)
    if table == "flights":
        df = df.rename(columns={"from":"from_location","to":"to_location",
                                "flightType":"flight_type","time":"travel_time","date":"travel_date"})
    elif table == "hotels":
        df = df.rename(columns={"name":"hotel_name","date":"travel_date"})
    elif table == "users":
        df = df.rename(columns={"code":"user_code"})
    return df

def store_prediction(payload, predicted_price):
    engine = mysql_engine()
    if engine is None:
        return False
    sql = text("""INSERT INTO prediction_history
    (from_location,to_location,flight_type,agency,travel_time,distance,predicted_price)
    VALUES (:from_location,:to_location,:flight_type,:agency,:travel_time,:distance,:predicted_price)""")
    with engine.begin() as conn:
        conn.execute(sql, {**payload, "predicted_price": float(predicted_price)})
    return True

def store_recommendation(destination, days, budget, count):
    engine = mysql_engine()
    if engine is None:
        return False
    sql = text("""INSERT INTO recommendation_history
    (destination,days,max_budget,result_count) VALUES (:d,:days,:budget,:count)""")
    with engine.begin() as conn:
        conn.execute(sql, {"d":destination,"days":int(days),"budget":budget,"count":int(count)})
    return True
