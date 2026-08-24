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

API_BASE_URL = st.secrets.get("API_BASE_URL", "http://127.0.0.1:8000")

# قاموس الترجمات متوافق 100% مع الموافقة الأخلاقية
translations = {
    "English": {
        "title": "PMOS Academic Productivity Tracker",
        "intro": "Welcome. Please enter your daily data to help us analyze productivity. All data is anonymous.",
        "participant_code": "Participant Code (e.g., A123)",
        "age": "Age (Must be 18-30)",
        "consent": "I have read and agree to the Informed Volunteer Consent Form.",
        "pmos_check": "Have you been diagnosed with PMOS (formerly PCOS) by a specialist doctor?",
        "productivity_section": "Module 1: Academic Productivity",
        "productivity_score": "Overall Academic Productivity Today (1 Very Unproductive - 10 Very Productive)",
        "sleep_section": "Module 2: Sleep & Physical State",
        "sleep_hours": "Sleep Hours Last Night",
        "fatigue_level": "Fatigue Level (1 Not tired at all - 5 Very tired)",
        "mood_section": "Module 3: Mood & Stress",
        "mood_status": "Today's Mood",
        "moods": ["Happy", "Calm", "Energetic", "Anxious", "Sad", "Angry", "Tired"],
        "stress_level": "Stress Level (1 Not stressed at all - 5 Very stressed)",
        "study_section": "Module 4: Study & Focus",
        "study_hours": "Total Study Hours Today",
        "focus_level": "Focus Level (1 Could not focus - 5 Completely focused)",
        "lifestyle_section": "Module 5: Lifestyle & Activity",
        "diet": "Dietary Habits (Healthy/Balanced meals today?)",
        "diet_options": ["Yes", "Partially", "No"],
        "exercise": "Did you do any physical activity/exercise today?",
        "exercise_duration": "If Yes, duration (in minutes)?",
        "submit": "Submit Data",
        "success": "Data submitted and saved successfully! Thank you.",
        "error_required": "⚠️ Please fill in your Participant Code and agree to the consent form!",
        "error_sub": "Error occurred while submitting data.",
        "error_conn": "Cannot connect to the server. Make sure FastAPI is running."
    },
    "العربية": {
        "title": "متتبع الإنتاجية الأكاديمية (PMOS)",
        "intro": "أهلاً بكِ. يرجى إدخال بياناتك اليومية. جميع البيانات سرية ومجهولة المصدر.",
        "participant_code": "رمز المشاركة (مثال: A123)",
        "age": "العمر (يجب أن يكون بين 18-30)",
        "consent": "لقد قرأت وأوافق على نموذج الموافقة المستنيرة للمشاركة التطوعية.",
        "pmos_check": "هل تم تشخيصك بمتلازمة PMOS (المعروفة سابقاً بـ PCOS) من قبل طبيب مختص؟",
        "productivity_section": "الوحدة 1: الإنتاجية الأكاديمية",
        "productivity_score": "تقييمك لإنتاجيتك الأكاديمية اليوم (1 ضعيف جداً - 10 ممتاز)",
        "sleep_section": "الوحدة 2: النوم والحالة البدنية",
        "sleep_hours": "ساعات النوم الليلة الماضية",
        "fatigue_level": "مستوى التعب (1 لست متعبة أبداً - 5 متعبة جداً)",
        "mood_section": "الوحدة 3: الحالة المزاجية والضغط النفسي",
        "mood_status": "الحالة المزاجية اليوم",
        "moods": ["سعيدة", "هادئة", "نشيطة", "قلقة", "حزينة", "غاضبة", "متعبة"],
        "stress_level": "مستوى الضغط النفسي (1 لا يوجد ضغط - 5 ضغط شديد)",
        "study_section": "الوحدة 4: الدراسة والتركيز",
        "study_hours": "إجمالي ساعات الدراسة اليوم",
        "focus_level": "مستوى التركيز (1 لم أستطع التركيز - 5 تركيز تام)",
        "lifestyle_section": "الوحدة 5: نمط الحياة والنشاط",
        "diet": "النظام الغذائي (هل تناولتي وجبات صحية/متوازنة اليوم؟)",
        "diet_options": ["نعم", "جزئياً", "لا"],
        "exercise": "هل مارستي أي نشاط بدني/رياضة اليوم؟",
        "exercise_duration": "إذا كانت الإجابة نعم، ما هي المدة (بالدقائق)؟",
        "submit": "إرسال البيانات",
        "success": "تم إرسال بياناتك وحفظها بنجاح! شكراً لكِ.",
        "error_required": "⚠️ يرجى إدخال رمز المشاركة والموافقة على نموذج المشاركة!",
        "error_sub": "حدث خطأ أثناء إرسال البيانات.",
        "error_conn": "لا يمكن الاتصال بالسيرفر. تأكدي من أن الخادم يعمل."
    },
    "Türkçe": {
        "title": "PMOS Akademik Verimlilik Takibi",
        "intro": "Hoş geldiniz. Lütfen günlük verilerinizi girin. Tüm veriler anonimdir.",
        "participant_code": "Katılımcı Kodu (örn. A123)",
        "age": "Yaş (18-30 arası olmalıdır)",
        "consent": "Bilgilendirilmiş Gönüllü Olur Formu'nu okudum ve onaylıyorum.",
        "pmos_check": "Bir uzman hekim tarafından PMOS (eski adıyla PCOS) tanısı aldınız mı?",
        "productivity_section": "Modül 1: Akademik Verimlilik",
        "productivity_score": "Bugünkü Genel Akademik Verimlilik Puanı (1 Çok Verimsiz - 10 Çok Verimli)",
        "sleep_section": "Modül 2: Uyku ve Fiziksel Durum",
        "sleep_hours": "Dün Geceki Uyku Saatleri",
        "fatigue_level": "Yorgunluk Seviyesi (1 Hiç yorgun değilim - 5 Çok yorgunum)",
        "mood_section": "Modül 3: Ruh Hâli ve Stres",
        "mood_status": "Bugünkü Ruh Hâli",
        "moods": ["Mutlu", "Sakin", "Enerjik", "Endişeli", "Üzgün", "Öfkeli", "Yorgun"],
        "stress_level": "Stres Seviyesi (1 Hiç stresli değilim - 5 Çok stresliyim)",
        "study_section": "Modül 4: Çalışma ve Odaklanma",
        "study_hours": "Bugün Ders Çalışmaya Ayrılan Toplam Süre (Saat)",
        "focus_level": "Odaklanma Seviyesi (1 Hiç odaklanamadım - 5 Tamamen odaklandım)",
        "lifestyle_section": "Modül 5: Yaşam Tarzı ve Aktivite",
        "diet": "Beslenme Düzeni (Bugün sağlıklı/dengeli beslendiniz mi?)",
        "diet_options": ["Evet", "Kısmen", "Hayır"],
        "exercise": "Bugün fiziksel aktivite/egzersiz yaptınız mı?",
        "exercise_duration": "Evet ise süresi (dakika)?",
        "submit": "Verileri Gönder",
        "success": "Veriler başarıyla gönderildi ve kaydedildi! Teşekkürler.",
        "error_required": "⚠️ Lütfen Katılımcı Kodunu girin ve onam formunu onaylayın!",
        "error_sub": "Veriler gönderilirken bir hata oluştu.",
        "error_conn": "Sunucuya bağlanılamıyor. Sunucunun çalıştığından emin olun."
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
        [data-testid="block-container"] p, h1, h2, h3, label, span {
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
    st.subheader("Registration / Screening")
    participant_code = st.text_input(t["participant_code"])
    age = st.number_input(t["age"], min_value=18, max_value=30, value=20)
    has_pmos = st.selectbox(t["pmos_check"], ["Yes / نعم / Evet", "No / لا / Hayır"])
    consent_given = st.checkbox(t["consent"])
    
    st.markdown("---")

    st.subheader(t["productivity_section"])
    productivity_score = st.slider(t["productivity_score"], 1, 10, 5)

    st.subheader(t["sleep_section"])
    sleep_hours = st.slider(t["sleep_hours"], 0.0, 24.0, 7.0, step=0.5)
    fatigue_level = st.slider(t["fatigue_level"], 1, 5, 3)

    st.subheader(t["mood_section"])
    mood_status = st.selectbox(t["mood_status"], t["moods"])
    stress_level = st.slider(t["stress_level"], 1, 5, 3)

    st.subheader(t["study_section"])
    study_hours = st.slider(t["study_hours"], 0.0, 24.0, 2.0, step=0.5)
    focus_level = st.slider(t["focus_level"], 1, 5, 3)

    st.subheader(t["lifestyle_section"])
    dietary_habits = st.selectbox(t["diet"], t["diet_options"])
    exercised_today = st.selectbox(t["exercise"], ["Yes / نعم / Evet", "No / لا / Hayır"])
    exercise_duration = st.number_input(t["exercise_duration"], min_value=0, value=0, step=10)

    submitted = st.form_submit_button(t["submit"])

if submitted:
    if not participant_code.strip() or not consent_given:
        st.error(t["error_required"])
    else:
        # تجهيز البيانات للإرسال للسيرفر
        data = {
            "participant_code": participant_code, 
            "age": age, 
            "consent_given": consent_given,
            "has_pmos": True if "Yes" in has_pmos else False,
            "productivity_score": productivity_score, 
            "sleep_hours": sleep_hours,
            "fatigue_level": fatigue_level, 
            "mood_status": mood_status, 
            "stress_level": stress_level,
            "study_hours": study_hours, 
            "focus_level": focus_level, 
            "dietary_habits": dietary_habits, 
            "exercised_today": True if "Yes" in exercised_today else False,
            "exercise_duration": exercise_duration
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/add_student", json=data, timeout=30)
            if response.status_code == 200:
                st.success(t["success"])
            else:
                st.error(f"{t['error_sub']} (Status Code: {response.status_code})")
        except requests.exceptions.RequestException:
            st.error(t["error_conn"])