import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Admin Dashboard", layout="wide")

st.title("Admin Dashboard - PMOS Tracker")
st.write("This is your private dashboard to view and analyze the data.")

if st.button("Refresh Data"):
    try:
        response = requests.get("http://127.0.0.1:8000/get_students")
        if response.status_code == 200:
            records = response.json().get("data", [])
            
            if records:
                df = pd.DataFrame(records)
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Students Logged", len(df))
                if "study_hours" in df.columns:
                    col2.metric("Average Study Hours", round(df["study_hours"].mean(), 1))
                if "focus_level" in df.columns:
                    col3.metric("Average Focus Level", round(df["focus_level"].mean(), 1))
                
                st.divider()
                
                st.subheader("Study Hours vs Focus Level")
                if "student_id" in df.columns and "study_hours" in df.columns and "focus_level" in df.columns:
                    chart_data = df.set_index("student_id")[["study_hours", "focus_level"]]
                    st.bar_chart(chart_data)
                
                st.subheader("Raw Data Table")
                st.dataframe(df)
            else:
                st.info("No data available yet.")
        else:
            st.error("Failed to fetch data from the server.")
    except:
        st.error("Cannot connect to the server. Make sure FastAPI is running.")