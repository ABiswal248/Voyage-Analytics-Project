import os
from datetime import date
import requests
import streamlit as st
from src.data_access import read_table, store_recommendation

st.set_page_config(page_title="Voyage Analytics",page_icon="✈️",layout="wide")
st.title("Voyage Analytics")
st.caption("Travel analytics, flight-price estimation, and hotel recommendations")
tab1,tab2,tab3=st.tabs(["Flight Price Prediction","Hotel Recommendation","Data Insights"])

with tab1:
    st.subheader("Estimate a flight price")
    try:
        flights=read_table("flights","flights.csv")
        flights=flights.rename(columns={"from":"from_location","to":"to_location","flightType":"flight_type","time":"travel_time","date":"travel_date"})
        origins=sorted(flights["from_location"].dropna().unique().tolist())
        destinations=sorted(flights["to_location"].dropna().unique().tolist())
        types=sorted(flights["flight_type"].dropna().unique().tolist())
        agencies=sorted(flights["agency"].dropna().unique().tolist())
    except Exception as e:
        st.error(f"Cannot load flights data: {e}"); origins=destinations=types=agencies=[]
    with st.form("flight_form"):
        c1,c2=st.columns(2)
        origin=c1.selectbox("Origin",origins)
        destination=c2.selectbox("Destination",destinations)
        flight_type=c1.selectbox("Flight type",types)
        agency=c2.selectbox("Agency",agencies)
        travel_time=st.number_input("Travel time (dataset units)",min_value=0.01,value=1.5,step=0.1)
        distance=st.number_input("Distance (dataset units)",min_value=0.01,value=500.0,step=10.0)
        travel_date=st.date_input("Travel date",value=date.today())
        submit=st.form_submit_button("Predict price")
    if submit:
        payload={"from_location":origin,"to_location":destination,"flight_type":flight_type,"agency":agency,"travel_time":travel_time,"distance":distance,"travel_date":str(travel_date)}
        try:
            r=requests.post(os.getenv("FLASK_URL","http://127.0.0.1:5000")+"/predict",json=payload,timeout=30)
            if r.ok:
                out=r.json(); st.success(f"Estimated price: {out['predicted_price']:.2f} ({out.get('currency','dataset units')})")
                st.caption("Prediction history stored in MySQL: "+str(out.get("saved_to_mysql",False)))
            else: st.error(r.json().get("error",r.text))
        except requests.RequestException:
            st.error("Cannot reach Flask API. Start it in another terminal with: python app.py")

with tab2:
    st.subheader("Find hotel options")
    try:
        hotels=read_table("hotels","hotels.csv")
        hotels=hotels.rename(columns={"name":"hotel_name"})
        places=sorted(hotels["place"].dropna().unique().tolist())
        with st.form("hotel_form"):
            dest=st.selectbox("Destination",places)
            days=st.number_input("Length of stay (days)",min_value=1,max_value=60,value=3)
            budget=st.number_input("Maximum total budget (dataset units)",min_value=0.0,value=1500.0,step=50.0)
            hsubmit=st.form_submit_button("Recommend hotels")
        if hsubmit:
            options=hotels[hotels["place"].eq(dest)].copy()
            options=options[options["days"].eq(days)]
            options=options[options["total"].le(budget)]
            options=options.sort_values(["total","price"]).drop_duplicates(subset=["hotel_name","place","days"])
            st.write(f"Found {len(options)} matching hotel options.")
            if options.empty: st.info("No exact match. Increase budget or change stay duration.")
            else: st.dataframe(options[["hotel_name","place","days","price","total"]].head(10),use_container_width=True)
            try: store_recommendation(dest,days,budget,len(options))
            except Exception: pass
    except Exception as e:
        st.error(f"Cannot load hotel data: {e}")

with tab3:
    st.subheader("Dataset overview")
    for table,csv in [("flights","flights.csv"),("hotels","hotels.csv"),("users","users.csv")]:
        try:
            df=read_table(table,csv)
            with st.expander(table.title()):
                st.metric("Rows",f"{len(df):,}")
                st.metric("Columns",len(df.columns))
                st.write("Missing values by column")
                st.dataframe(df.isna().sum().rename("missing").to_frame())
                st.dataframe(df.head(10),use_container_width=True)
        except Exception as e: st.warning(f"{table}: {e}")
