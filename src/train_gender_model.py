from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from src.data_access import read_table, ROOT

ART=ROOT/"artifacts"; ART.mkdir(exist_ok=True)
df=read_table("users","users.csv").rename(columns={"code":"user_code"})
# This is an educational demonstration of the brief's classification objective.
# Exclude 'none' because it is not a reliable binary target class; keep the real label in the source table.
df=df[df["gender"].astype(str).str.lower().isin(["male","female"])].copy()
if df["gender"].nunique()<2: raise ValueError("Need male and female labels in users data.")
features=["company","age"]; target="gender"
X=df[features]; y=df[target].astype(str).str.lower()
X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.2,random_state=42,stratify=y)
pre=ColumnTransformer([
 ("company",Pipeline([("imputer",SimpleImputer(strategy="most_frequent")),("onehot",OneHotEncoder(handle_unknown="ignore"))]),["company"]),
 ("age",Pipeline([("imputer",SimpleImputer(strategy="median"))]),["age"])
])
pipe=Pipeline([("preprocessor",pre),("model",RandomForestClassifier(n_estimators=120,random_state=42,class_weight="balanced"))])
pipe.fit(X_train,y_train); pred=pipe.predict(X_test)
print("Accuracy:",round(accuracy_score(y_test,pred),4))
print(classification_report(y_test,pred,zero_division=0))
joblib.dump({"model":pipe,"features":features},ART/"gender_model.joblib")
print("Saved artifacts/gender_model.joblib")
print("Caution: this is a coursework demonstration; demographic inference may be inaccurate and should not be used for real-world decisions.")
