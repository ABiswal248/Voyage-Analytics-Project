from pathlib import Path
from datetime import datetime
import joblib
import pandas as pd
from flask import Flask, request, jsonify
from src.data_access import ROOT, store_prediction

app=Flask(__name__)
MODEL_PATH=ROOT/"artifacts"/"flight_price_model.joblib"
def load_model():
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)

@app.get("/")
def home():
    return jsonify({"app":"Voyage Analytics API","status":"running","endpoints":["/health","/predict"]})

@app.get("/health")
def health():
    return jsonify({"status":"ok","model_loaded":MODEL_PATH.exists()})

@app.post("/predict")
def predict():
    bundle=load_model()
    if bundle is None:
        return jsonify({"error":"Model not found. Run: python -m src.train_flight_model"}), 503
    data=request.get_json(silent=True) or {}
    required=["from_location","to_location","flight_type","agency","travel_time","distance"]
    missing=[k for k in required if k not in data]
    if missing: return jsonify({"error":"Missing fields","fields":missing}),400
    try:
        date=pd.to_datetime(data.get("travel_date",datetime.now().date()),errors="raise")
        row=pd.DataFrame([{
          "from_location":data["from_location"],"to_location":data["to_location"],
          "flight_type":data["flight_type"],"agency":data["agency"],
          "travel_time":float(data["travel_time"]),"distance":float(data["distance"]),
          "travel_year":date.year,"travel_month":date.month,"travel_day":date.day
        }],columns=bundle["features"])
        value=float(bundle["model"].predict(row)[0])
        payload={k:data[k] for k in required}
        try: stored=store_prediction(payload,value)
        except Exception as exc:
            print("[WARN] Prediction succeeded but DB history insert failed:",exc); stored=False
        return jsonify({"predicted_price":round(value,2),"currency":"dataset units","saved_to_mysql":stored})
    except (ValueError,TypeError) as exc:
        return jsonify({"error":f"Invalid input: {exc}"}),400

if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000,debug=False)
