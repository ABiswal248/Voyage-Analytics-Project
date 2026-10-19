from pathlib import Path
import matplotlib.pyplot as plt
from src.data_access import read_table, ROOT
REPORT=ROOT/"reports"; REPORT.mkdir(exist_ok=True)
for table,csv in [("flights","flights.csv"),("hotels","hotels.csv"),("users","users.csv")]:
    df=read_table(table,csv)
    print(f"\n===== {table.upper()} =====")
    print("Shape:",df.shape)
    print("\nData types:\n",df.dtypes)
    print("\nMissing values:\n",df.isna().sum())
    print("\nDuplicates:",df.duplicated().sum())
    print("\nSample:\n",df.head())
    df.describe(include="all").transpose().to_csv(REPORT/f"{table}_summary.csv")
flights=read_table("flights","flights.csv")
flights=flights.rename(columns={"from":"from_location","to":"to_location","flightType":"flight_type","time":"travel_time"})
plt.figure(figsize=(8,5)); flights["price"].hist(bins=40); plt.title("Flight Price Distribution"); plt.xlabel("Price (dataset units)"); plt.ylabel("Count"); plt.tight_layout(); plt.savefig(REPORT/"flight_price_distribution.png"); plt.close()
plt.figure(figsize=(8,5)); flights.groupby("flight_type")["price"].mean().sort_values().plot(kind="bar"); plt.title("Average Flight Price by Type"); plt.ylabel("Average price (dataset units)"); plt.tight_layout(); plt.savefig(REPORT/"average_price_by_flight_type.png"); plt.close()
print(f"\nEDA reports saved to {REPORT}")
