from datetime import date

import joblib
import pandas as pd
import streamlit as st

from src.data_access import (
    ROOT,
    read_table,
    store_prediction,
    store_recommendation,
)

MODEL_PATH = ROOT / "artifacts" / "flight_price_model.joblib"


@st.cache_resource
def load_flight_model():
    """Load the trained flight-price model once per Streamlit session."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Flight model not found: {MODEL_PATH}")
    return joblib.load(MODEL_PATH)


st.set_page_config(
    page_title="Voyage Analytics",
    page_icon="✈️",
    layout="wide",
)
st.title("Voyage Analytics")
st.caption("Travel analytics, flight-price estimation, and hotel recommendations")

tab1, tab2, tab3 = st.tabs(
    ["Flight Price Prediction", "Hotel Recommendation", "Data Insights"]
)

with tab1:
    st.subheader("Estimate a flight price")

    try:
        flights = read_table("flights", "flights.csv")
        flights = flights.rename(
            columns={
                "from": "from_location",
                "to": "to_location",
                "flightType": "flight_type",
                "time": "travel_time",
                "date": "travel_date",
            }
        )
        origins = sorted(flights["from_location"].dropna().unique().tolist())
        destinations = sorted(flights["to_location"].dropna().unique().tolist())
        types = sorted(flights["flight_type"].dropna().unique().tolist())
        agencies = sorted(flights["agency"].dropna().unique().tolist())
    except Exception as exc:
        st.error(f"Cannot load flights data: {exc}")
        origins = destinations = types = agencies = []

    if not all([origins, destinations, types, agencies]):
        st.warning("Flight prediction inputs are unavailable because flight data could not be loaded.")
    else:
        with st.form("flight_form"):
            col1, col2 = st.columns(2)
            origin = col1.selectbox("Origin", origins)
            destination = col2.selectbox("Destination", destinations)
            flight_type = col1.selectbox("Flight type", types)
            agency = col2.selectbox("Agency", agencies)
            travel_time = st.number_input(
                "Travel time (dataset units)",
                min_value=0.01,
                value=1.5,
                step=0.1,
            )
            distance = st.number_input(
                "Distance (dataset units)",
                min_value=0.01,
                value=500.0,
                step=10.0,
            )
            travel_date = st.date_input("Travel date", value=date.today())
            submit = st.form_submit_button("Predict price")

        if submit:
            try:
                bundle = load_flight_model()
                travel_dt = pd.to_datetime(travel_date, errors="raise")

                prediction_payload = {
                    "from_location": origin,
                    "to_location": destination,
                    "flight_type": flight_type,
                    "agency": agency,
                    "travel_time": float(travel_time),
                    "distance": float(distance),
                }

                model_row = pd.DataFrame(
                    [{
                        **prediction_payload,
                        "travel_year": travel_dt.year,
                        "travel_month": travel_dt.month,
                        "travel_day": travel_dt.day,
                    }],
                    columns=bundle["features"],
                )

                predicted_price = float(
                    bundle["model"].predict(model_row)[0]
                )

                st.success(
                    f"Estimated price: {predicted_price:.2f} "
                    "(dataset units)"
                )

                try:
                    saved = store_prediction(
                        prediction_payload,
                        round(predicted_price, 2),
                    )
                except Exception:
                    saved = False

                st.caption(
                    f"Prediction history stored in MySQL: {saved}"
                )

            except FileNotFoundError as exc:
                st.error(str(exc))
            except Exception as exc:
                st.error(
                    f"Flight prediction failed: "
                    f"{type(exc).__name__}: {exc}"
                )
