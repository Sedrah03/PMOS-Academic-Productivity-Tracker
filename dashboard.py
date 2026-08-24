import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Admin Dashboard", layout="wide")

st.title("Admin Dashboard - PMOS Tracker")
st.write("This is your private dashboard to view and analyze the data.")

# 1. التعديل الأول: حماية الرابط واستدعاؤه من الأسرار (Secrets)
# إذا لم يجد الرابط في الأسرار (على السيرفر)، سيستخدم الرابط المحلي للتشغيل على جهازك
API_BASE_URL = st.secrets.get("API_BASE_URL", "http://127.0.0.1:8000")

# أضيفي هذا الكود تحت تعريف API_BASE_URL مباشرة

@st.cache_data(ttl=300) # ttl=300 تعني: احتفظ بالبيانات في الذاكرة لمدة 300 ثانية (5 دقائق)
def fetch_data():
    response = requests.get(f"{API_BASE_URL}/get_students", timeout=30)
    if response.status_code == 200:
        return response.json().get("data", [])
    return None


if st.button("Refresh Data"):
    try:
        # 2. التعديل الثاني: استخدام الرابط الديناميكي بدلاً من الرابط الثابت
        response = requests.get(f"{API_BASE_URL}/get_students", timeout=30)
        
        if response.status_code == 200:
            records = response.json().get("data", [])
            
            if records:
                # تحويل البيانات القادمة من السيرفر إلى جدول (DataFrame) يسهل تحليله
                df = pd.DataFrame(records)
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Students Logged", len(df))
                
                if "study_hours" in df.columns:
                    col2.metric("Average Study Hours", round(df["study_hours"].mean(), 1))
                if "focus_level" in df.columns:
                    col3.metric("Average Focus Level", round(df["focus_level"].mean(), 1))
                
                st.divider()
                
                st.subheader("Study Hours vs Focus Level")
                # 3. التعديل الثالث: استخدام participant_code ليكون المحور الأساسي (Index) للرسم البياني
                if "participant_code" in df.columns and "study_hours" in df.columns and "focus_level" in df.columns:
                    chart_data = df.set_index("participant_code")[["study_hours", "focus_level"]]
                    st.bar_chart(chart_data)
                
                st.subheader("Raw Data Table")
                st.dataframe(df)
            else:
                st.info("No data available yet.")
        else:
            st.error(f"Failed to fetch data from the server. Status Code: {response.status_code}")
    except requests.exceptions.RequestException:
        st.error("Cannot connect to the server. Make sure FastAPI is running.")