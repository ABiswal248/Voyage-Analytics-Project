from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor, ExtraTreesRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from src.data_access import read_table, ROOT

ART=ROOT/"artifacts"; REPORT=ROOT/"reports"
ART.mkdir(exist_ok=True); REPORT.mkdir(exist_ok=True)

df=read_table("flights","flights.csv")
# Normalize column names for either MySQL or CSV mode.
df=df.rename(columns={"from":"from_location","to":"to_location","flightType":"flight_type","time":"travel_time","date":"travel_date"})
df["travel_date"]=pd.to_datetime(df["travel_date"], errors="coerce")
df["travel_year"]=df["travel_date"].dt.year
df["travel_month"]=df["travel_date"].dt.month
df["travel_day"]=df["travel_date"].dt.day
features=["from_location","to_location","flight_type","agency","travel_time","distance","travel_year","travel_month","travel_day"]
target="price"
df=df.dropna(subset=[target])
X=df[features]; y=df[target].astype(float)
cat=["from_location","to_location","flight_type","agency"]
num=["travel_time","distance","travel_year","travel_month","travel_day"]
pre=ColumnTransformer([
 ("categorical",Pipeline([("imputer",SimpleImputer(strategy="most_frequent")),("onehot",OneHotEncoder(handle_unknown="ignore"))]),cat),
 ("numeric",Pipeline([("imputer",SimpleImputer(strategy="median"))]),num)
])
X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.2,random_state=42)
models={
 "RandomForest":RandomForestRegressor(n_estimators=160,min_samples_leaf=2,n_jobs=-1,random_state=42),
 "ExtraTrees":ExtraTreesRegressor(n_estimators=160,min_samples_leaf=2,n_jobs=-1,random_state=42)
}
results=[]; best=None; best_rmse=float("inf")
for name, estimator in models.items():
    pipe=Pipeline([("preprocessor",pre),("model",estimator)])
    pipe.fit(X_train,y_train)
    pred=pipe.predict(X_test)
    rmse=float(np.sqrt(mean_squared_error(y_test,pred)))
    row={"model":name,"MAE":float(mean_absolute_error(y_test,pred)),"RMSE":rmse,"R2":float(r2_score(y_test,pred))}
    results.append(row); print(row)
    if rmse<best_rmse:
        best_rmse=rmse; best=pipe
joblib.dump({"model":best,"features":features},ART/"flight_price_model.joblib")
pd.DataFrame(results).to_csv(REPORT/"flight_model_metrics.csv",index=False)
print(f"\nSaved best model to {ART/'flight_price_model.joblib'}")
print(pd.DataFrame(results).sort_values("RMSE").to_string(index=False))
# Optional MLflow experiment tracking (will create local mlruns folder).
try:
    import mlflow
    mlflow.set_experiment("Voyage Analytics - Flight Price")
    for row in results:
        with mlflow.start_run(run_name=row["model"]):
            mlflow.log_param("model",row["model"])
            mlflow.log_metrics({"MAE":row["MAE"],"RMSE":row["RMSE"],"R2":row["R2"]})
except Exception as exc:
    print(f"[INFO] MLflow tracking skipped: {exc}")
