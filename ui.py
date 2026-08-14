import streamlit as st
import requests

# إخفاء القائمة العلوية وشريط Streamlit تماماً
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# قاموس الترجمات بعد التحديث إلى PMOS
translations = {
    "English": {
        "title": "PMOS Academic Productivity Tracker",
        "intro": "Welcome. Please enter your daily data to help us analyze productivity:",
        "student_id": "Student ID",
        "age": "Age",
        "uni_year": "University Year",
        "academic_section": "Academic & Health Metrics",
        "study_hours": "Study Hours Today",
        "focus_level": "Focus Level (1 Poor - 10 Excellent)",
        "classes_attended": "Classes Attended",
        "assignments": "Assignments Completed",
        "sleep_hours": "Sleep Hours",
        "fatigue_level": "Fatigue Level (1 Energetic - 10 Exhausted)",
        "mood_status": "Mood Status",
        "moods": ["Stable", "Stressed", "Depressed", "Happy"],
        "pmos_check": "Have you been diagnosed with PMOS?",
        "symptoms_section": "Clinical PMOS Symptoms (Scale 0-10)",
        "acne": "Acne Severity",
        "pelvic_pain": "Pelvic Pain Level",
        "hair_loss": "Hair Loss Level",
        "weight_gain": "Weight Fluctuation",
        "submit": "Submit Data",
        "success": "Data submitted and saved successfully! Thank you.",
        "error_id": "⚠️ Please fill in all necessary fields. Student ID is required!",
        "error_sub": "Error occurred while submitting data.",
        "error_conn": "Cannot connect to the server. Make sure FastAPI is running."
    },
    "العربية": {
        "title": "متتبع الإنتاجية الأكاديمية (PMOS)",
        "intro": "أهلاً بكِ. يرجى إدخال بياناتك اليومية لمساعدتنا في تحليل الإنتاجية:",
        "student_id": "رقم الطالبة",
        "age": "العمر",
        "uni_year": "السنة الدراسية",
        "academic_section": "المقاييس الأكاديمية والصحية",
        "study_hours": "ساعات الدراسة اليوم",
        "focus_level": "مستوى التركيز (1 ضعيف - 10 ممتاز)",
        "classes_attended": "عدد المحاضرات التي حضرتها",
        "assignments": "عدد الواجبات المنجزة",
        "sleep_hours": "ساعات النوم",
        "fatigue_level": "مستوى التعب الجسدي (1 نشيطة - 10 متعبة جداً)",
        "mood_status": "الحالة المزاجية",
        "moods": ["مستقرة", "متوترة", "محبطة", "سعيدة"],
        "pmos_check": "هل تم تشخيصك بمتلازمة (PMOS)؟",
        "symptoms_section": "أعراض PMOS (مقياس 0-10)",
        "acne": "شدة حب الشباب",
        "pelvic_pain": "مستوى ألم الحوض",
        "hair_loss": "مستوى تساقط أو خفة الشعر",
        "weight_gain": "تغيرات الوزن أو صعوبة نزوله",
        "submit": "إرسال البيانات",
        "success": "تم إرسال بياناتك وحفظها بنجاح! شكراً لكِ.",
        "error_id": "⚠️ يرجى تعبئة الحقول الضرورية. رقم الطالبة مطلوب!",
        "error_sub": "حدث خطأ أثناء إرسال البيانات.",
        "error_conn": "لا يمكن الاتصال بالسيرفر. تأكدي من أن FastAPI يعمل."
    },
    "Türkçe": {
        "title": "PMOS Akademik Verimlilik Takibi",
        "intro": "Hoş geldiniz. Verimliliği analiz etmemize yardımcı olmak için lütfen günlük verilerinizi girin:",
        "student_id": "Öğrenci Numarası",
        "age": "Yaş",
        "uni_year": "Üniversite Yılı",
        "academic_section": "Akademik ve Sağlık Metrikleri",
        "study_hours": "Bugünkü Çalışma Saatleri",
        "focus_level": "Odaklanma Seviyesi (1 Zayıf - 10 Mükemmel)",
        "classes_attended": "Katılınan Ders Sayısı",
        "assignments": "Tamamlanan Ödevler",
        "sleep_hours": "Uyku Saatleri",
        "fatigue_level": "Yorgunluk Seviyesi (1 Dinamik - 10 Bitkin)",
        "mood_status": "Ruh Hali",
        "moods": ["Stabil", "Stresli", "Depresif", "Mutlu"],
        "pmos_check": "PMOS teşhisi konuldu mu?",
        "symptoms_section": "Spesifik PMOS Belirtileri (Ölçek 0-10)",
        "acne": "Akne Şiddeti",
        "pelvic_pain": "Pelvik Ağrı Seviyesi",
        "hair_loss": "Saç Dökülmesi Seviyesi",
        "weight_gain": "Kilo Dalgalanması",
        "submit": "Verileri Gönder",
        "success": "Veriler başarıyla gönderildi ve kaydedildi! Teşekkürler.",
        "error_id": "⚠️ Lütfen gerekli tüm alanları doldurun. Öğrenci Numarası gereklidir!",
        "error_sub": "Veriler gönderilirken bir hata oluştu.",
        "error_conn": "Sunucuya bağlanılamıyor. FastAPI'nin çalıştığından emin olun."
    }
}

col1, col2 = st.columns([8, 2])
with col2:
    lang = st.selectbox("Language", ["English", "العربية", "Türkçe"], label_visibility="collapsed")

t = translations[lang]

if lang == "العربية":
    st.markdown(
        """
        <style>
        [data-testid="block-container"] { direction: rtl; }
        [data-testid="block-container"] p, 
        [data-testid="block-container"] h1, 
        [data-testid="block-container"] h2, 
        [data-testid="block-container"] h3, 
        [data-testid="block-container"] label, 
        [data-testid="block-container"] span {
            text-align: right !important;
            font-family: 'Arial', sans-serif !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

st.title(t["title"])
st.write(t["intro"])

with st.form("student_form"):
    student_id = st.text_input(t["student_id"])
    age = st.number_input(t["age"], min_value=17, max_value=40, value=20)
    university_year = st.number_input(t["uni_year"], min_value=1, max_value=7, value=2)
    
    st.subheader(t["academic_section"])
    study_hours = st.slider(t["study_hours"], 0.0, 24.0, 2.0)
    focus_level = st.slider(t["focus_level"], 1, 10, 5)
    classes_attended = st.number_input(t["classes_attended"], min_value=0, max_value=10, value=0)
    assignments_completed = st.number_input(t["assignments"], min_value=0, max_value=10, value=0)
    sleep_hours = st.slider(t["sleep_hours"], 0.0, 24.0, 7.0)
    fatigue_level = st.slider(t["fatigue_level"], 1, 10, 5)
    mood_status = st.selectbox(t["mood_status"], t["moods"])
    
    has_pmos = st.checkbox(t["pmos_check"])
    
    st.subheader(t["symptoms_section"])
    acne_severity = st.slider(t["acne"], 0, 10, 0)
    pelvic_pain_level = st.slider(t["pelvic_pain"], 0, 10, 0)
    hair_loss_level = st.slider(t["hair_loss"], 0, 10, 0)
    weight_fluctuation = st.slider(t["weight_gain"], 0, 10, 0)
    
    submitted = st.form_submit_button(t["submit"])

if submitted:
    if not student_id.strip():
        st.error(t["error_id"])
    else:
        data = {
            "student_id": student_id, "age": age, "university_year": university_year,
            "study_hours": study_hours, "focus_level": focus_level, "classes_attended": classes_attended,
            "assignments_completed": assignments_completed, "sleep_hours": sleep_hours,
            "fatigue_level": fatigue_level, "mood_status": mood_status, "has_pmos": has_pmos,
            "acne_severity": acne_severity, "pelvic_pain_level": pelvic_pain_level,
            "hair_loss_level": hair_loss_level, "weight_fluctuation": weight_fluctuation
        }
        try:
            response = requests.post("http://127.0.0.1:8000/add_student", json=data)
            if response.status_code == 200:
                st.success(t["success"])
            else:
                st.error(t["error_sub"])
        except:
            st.error(t["error_conn"])