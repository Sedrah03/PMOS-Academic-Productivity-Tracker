import streamlit as st
import requests
import json

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

# قاموس الترجمات محدث بالكامل مع نصوص الموافقة
translations = {
    "English": {
        "title": "PMOS Academic Productivity Tracker",
        "intro": "Welcome. Please enter your daily data to help us analyze productivity. All data is anonymous.",
        "participant_code": "Participant Code (e.g., A123)",
        "age": "Age (Must be 18-30)",
        "consent_text": "I voluntarily agree to participate in this research. I understand my contact information will only be used to send the app link and for academic research purposes, processed in accordance with privacy standards.",
        "consent": "I agree to the Informed Volunteer Consent Form.",
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
        "error_conn": "Cannot connect to the server. Make sure FastAPI is running.",
        "error_auth": "🔒 Unauthorized access. Invalid API Key."
    },
    "العربية": {
        "title": "متتبع الإنتاجية الأكاديمية لمتلازمة المبيض الأيضية متعددة الغدد الصماء (PMOS)",
        "intro": "أهلاً بكِ. يرجى إدخال بياناتك اليومية لمساعدتنا في تحليل الإنتاجية. جميع البيانات سرية ومجهولة المصدر.",
        "participant_code": "رمز المشاركة (مثال: A123)",
        "age": "العمر (يجب أن يكون بين 18 و 30 عاماً)",
        "consent_text": "أوافق على المشاركة طوعاً في هذا البحث. أفهم أن بيانات التواصل الخاصة بي ستُستخدم فقط لإرسال رابط التطبيق ولأغراض البحث الأكاديمي، وستتم معالجتها وفقاً لمعايير الخصوصية.",
        "consent": "أوافق على نموذج الموافقة المستنيرة.",
        "pmos_check": "هل تم تشخيصك بمتلازمة المبيض الأيضية متعددة الغدد الصماء (PMOS) المعروفة سابقاً بمتلازمة تكيس المبايض (PCOS) من قبل طبيب مختص؟",
        "productivity_section": "الوحدة الأولى: الإنتاجية الأكاديمية",
        "productivity_score": "تقييمك لإنتاجيتك الأكاديمية اليوم (1 ضعيف جداً - 10 ممتاز)",
        "sleep_section": "الوحدة الثانية: النوم والحالة البدنية",
        "sleep_hours": "عدد ساعات النوم الليلة الماضية",
        "fatigue_level": "مستوى التعب (1 لست متعبة أبداً - 5 متعبة جداً)",
        "mood_section": "الوحدة الثالثة: الحالة المزاجية والضغط النفسي",
        "mood_status": "الحالة المزاجية اليوم",
        "moods": ["سعيدة", "هادئة", "نشيطة", "قلقة", "حزينة", "غاضبة", "متعبة"],
        "stress_level": "مستوى الضغط النفسي (1 لا يوجد ضغط - 5 ضغط شديد)",
        "study_section": "الوحدة الرابعة: الدراسة والتركيز",
        "study_hours": "إجمالي ساعات الدراسة اليوم",
        "focus_level": "مستوى التركيز (1 لم أستطع التركيز - 5 تركيز تام)",
        "lifestyle_section": "الوحدة الخامسة: نمط الحياة والنشاط البدني",
        "diet": "النظام الغذائي (هل تناولتي وجبات صحية ومتوازنة اليوم؟)",
        "diet_options": ["نعم", "جزئياً", "لا"],
        "exercise": "هل مارستي أي نشاط بدني أو رياضة اليوم؟",
        "exercise_duration": "إذا كانت الإجابة نعم، ما هي المدة بالدقائق؟",
        "submit": "إرسال البيانات",
        "success": "تم إرسال بياناتك وحفظها بنجاح! شكراً لكِ.",
        "error_required": "⚠️ يرجى إدخال رمز المشاركة والموافقة على نموذج الموافقة!",
        "error_sub": "حدث خطأ أثناء إرسال البيانات.",
        "error_conn": "لا يمكن الاتصال بالسيرفر. تأكدي من أن الخادم يعمل.",
        "error_auth": "🔒 وصول غير مصرح به. مفتاح API غير صالح."
    },
    "Türkçe": {
        "title": "PMOS Akademik Verimlilik Takibi",
        "intro": "Hoş geldiniz. Lütfen verimliliği analiz etmemize yardımcı olmak için günlük verilerinizi girin. Tüm veriler anonimdir.",
        "participant_code": "Katılımcı Kodu (örn. A123)",
        "age": "Yaş (18-30 arası olmalıdır)",
        "consent_text": "Bu araştırmaya gönüllü olarak katılmayı kabul ediyorum. İletişim bilgilerimin yalnızca uygulama bağlantısını iletmek ve akademik araştırma kapsamında kullanılacağını, verilerimin gizlilik standartlarına uygun işleneceğini anlıyorum.",
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
        "error_conn": "Sunucuya bağlanılamıyor. Sunucunun çalıştığından emin olun.",
        "error_auth": "🔒 Yetkisiz erişim. Geçersiz API anahtarı."
    }
}

col1, col2 = st.columns([8, 2])
with col2:
    lang = st.selectbox("Language", ["English", "العربية", "Türkçe"], label_visibility="collapsed")

t = translations[lang]

# ضبط اتجاه النص بالكامل بناءً على لغة القائمة المنسدلة
if lang == "العربية":
    st.markdown(
        """
        <style>
        [data-testid="block-container"] { direction: rtl; text-align: right; }
        .stTextInput, .stNumberInput, .stSelectbox, .stSlider, div[data-baseweb="select"] {
            direction: rtl !important;
            text-align: right !important;
        }
        label, p, span, h1, h2, h3 {
            direction: rtl !important;
            text-align: right !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <style>
        [data-testid="block-container"] { direction: ltr; text-align: left; }
        </style>
        """,
        unsafe_allow_html=True
    )

st.title(t["title"])
st.write(t["intro"])



with st.form("student_form"):
    st.subheader("Registration / Screening" if lang != "العربية" else "التسجيل والفحص المبدئي")
    participant_code = st.text_input(t["participant_code"])
    age = st.number_input(t["age"], min_value=18, max_value=30, value=20)
    has_pmos = st.selectbox(t["pmos_check"], ["Yes / نعم / Evet", "No / لا / Hayır"])
    
    # --- التعديل هنا: عرض نص الموافقة في صندوق بارز ثم زر الاختيار ---
    st.info(t["consent_text"])
    consent_given = st.checkbox(t["consent"])
    # ------------------------------------------------------------------
    
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
            clean_url = API_BASE_URL.strip().rstrip("/")
            ui_api_key = st.secrets.get("PROJECT_API_KEY", "").strip()
            
            ui_api_key = ui_api_key.encode('ascii', 'ignore').decode('ascii')
            
            headers = {
                "X-API-KEY": ui_api_key,
                "Content-Type": "application/json; charset=utf-8"
            }
            
            json_payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
            
            response = requests.post(f"{clean_url}/add_student", data=json_payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                st.success(t["success"])
            elif response.status_code == 401:
                st.error(t["error_auth"])
            else:
                st.error(f"{t['error_sub']} (Status Code: {response.status_code})")
                
        except requests.exceptions.RequestException:
            st.error(t["error_conn"])


# ==========================================
# شاشة الفحص المبدئي بالأعراض (PCOS Screening)
# ==========================================
screen_t = {
    "English": {
        "header": "Optional: Symptom Pattern Check",
        "intro": "Answer a few questions to see how your reported symptoms compare with patterns in a research dataset. This is not a diagnosis. Your answers here are not saved.",
        "age": "Age", "weight": "Weight (kg)", "height": "Height (cm)",
        "cycle": "Menstrual cycle", "cycle_opts": ["Regular", "Irregular"],
        "cycle_len": "Cycle length (days)",
        "q_wg": "Recent weight gain", "q_hg": "Unwanted hair growth",
        "q_sd": "Skin darkening (e.g., neck, underarms)", "q_hl": "Hair loss",
        "q_pm": "Pimples / acne", "q_ff": "Frequent fast food", "q_ex": "Regular exercise",
        "submit": "Check",
        "levels": {"low": "Low similarity", "moderate": "Moderate similarity", "high": "High similarity"},
        "msg": "Your reported symptoms show {level} to the patterns found in the research dataset. If you have health concerns, please consult a physician.",
        "disclaimer": "Research prototype only. Not a medical diagnosis.",
        "err_conn": "Cannot connect to the server. Please try again in a minute.",
        "err_auth": "Unauthorized access.", "err_other": "Something went wrong.",
    },
    "العربية": {
        "header": "اختياري: فحص نمط الأعراض",
        "intro": "أجيبي عن بعض الأسئلة لترين مدى تشابه الأعراض التي تذكرينها مع أنماط في قاعدة بيانات بحثية. هذا ليس تشخيصاً. إجاباتك هنا لا تُحفظ.",
        "age": "العمر", "weight": "الوزن (كغ)", "height": "الطول (سم)",
        "cycle": "الدورة الشهرية", "cycle_opts": ["منتظمة", "غير منتظمة"],
        "cycle_len": "مدة الدورة (أيام)",
        "q_wg": "زيادة حديثة في الوزن", "q_hg": "نمو شعر غير مرغوب",
        "q_sd": "اسمرار الجلد (مثل الرقبة أو تحت الإبط)", "q_hl": "تساقط الشعر",
        "q_pm": "حبوب / حب الشباب", "q_ff": "تناول متكرر للوجبات السريعة", "q_ex": "ممارسة الرياضة بانتظام",
        "submit": "افحصي",
        "levels": {"low": "تشابه منخفض", "moderate": "تشابه متوسط", "high": "تشابه مرتفع"},
        "msg": "الأعراض التي ذكرتيها تُظهر {level} مع الأنماط الموجودة في قاعدة البيانات البحثية. إذا كانت لديكِ مخاوف صحية، يُرجى استشارة طبيب.",
        "disclaimer": "نموذج بحثي أولي فقط. ليس تشخيصاً طبياً.",
        "err_conn": "لا يمكن الاتصال بالسيرفر. حاولي مجدداً بعد دقيقة.",
        "err_auth": "وصول غير مصرح به.", "err_other": "حدث خطأ ما.",
    },
    "Türkçe": {
        "header": "İsteğe bağlı: Belirti Örüntüsü Kontrolü",
        "intro": "Bildirdiğiniz belirtilerin bir araştırma veri setindeki örüntülerle ne kadar benzeştiğini görmek için birkaç soruyu yanıtlayın. Bu bir teşhis değildir. Buradaki yanıtlarınız kaydedilmez.",
        "age": "Yaş", "weight": "Kilo (kg)", "height": "Boy (cm)",
        "cycle": "Adet döngüsü", "cycle_opts": ["Düzenli", "Düzensiz"],
        "cycle_len": "Döngü uzunluğu (gün)",
        "q_wg": "Yakın zamanda kilo alımı", "q_hg": "İstenmeyen tüylenme",
        "q_sd": "Cilt koyulaşması (boyun, koltuk altı vb.)", "q_hl": "Saç dökülmesi",
        "q_pm": "Sivilce / akne", "q_ff": "Sık fast food tüketimi", "q_ex": "Düzenli egzersiz",
        "submit": "Kontrol Et",
        "levels": {"low": "Düşük benzerlik", "moderate": "Orta düzey benzerlik", "high": "Yüksek benzerlik"},
        "msg": "Bildirdiğiniz belirtiler, araştırma veri setindeki örüntülerle {level} göstermektedir. Sağlığınızla ilgili endişeleriniz varsa lütfen bir hekime danışın.",
        "disclaimer": "Yalnızca araştırma prototipi. Tıbbi teşhis değildir.",
        "err_conn": "Sunucuya bağlanılamıyor. Lütfen bir dakika sonra tekrar deneyin.",
        "err_auth": "Yetkisiz erişim.", "err_other": "Bir şeyler ters gitti.",
    },
}
ss = screen_t[lang]


def risk_level(p):
    if p < 0.35:
        return "low"
    elif p < 0.65:
        return "moderate"
    return "high"


st.markdown("---")
with st.expander(ss["header"]):
    st.caption(ss["intro"])
    with st.form("screening_form"):
        s_age = st.number_input(ss["age"], min_value=18, max_value=30, value=20)
        s_weight = st.number_input(ss["weight"], min_value=30.0, max_value=200.0, value=60.0, step=0.5)
        s_height = st.number_input(ss["height"], min_value=120.0, max_value=220.0, value=165.0, step=0.5)
        s_cycle = st.selectbox(ss["cycle"], ss["cycle_opts"])
        s_cycle_len = st.number_input(ss["cycle_len"], min_value=1, max_value=15, value=5)
        s_wg = st.checkbox(ss["q_wg"])
        s_hg = st.checkbox(ss["q_hg"])
        s_sd = st.checkbox(ss["q_sd"])
        s_hl = st.checkbox(ss["q_hl"])
        s_pm = st.checkbox(ss["q_pm"])
        s_ff = st.checkbox(ss["q_ff"])
        s_ex = st.checkbox(ss["q_ex"])
        s_submit = st.form_submit_button(ss["submit"])

    if s_submit:
        payload = {
            "age": int(s_age),
            "weight_kg": float(s_weight),
            "height_cm": float(s_height),
            "cycle_regular": s_cycle == ss["cycle_opts"][0],
            "cycle_length_days": int(s_cycle_len),
            "weight_gain": s_wg,
            "hair_growth": s_hg,
            "skin_darkening": s_sd,
            "hair_loss": s_hl,
            "pimples": s_pm,
            "fast_food": s_ff,
            "regular_exercise": s_ex,
        }
        try:
            base = API_BASE_URL.strip().rstrip("/")
            key = st.secrets.get("PROJECT_API_KEY", "").strip()
            key = key.encode("ascii", "ignore").decode("ascii")
            with st.spinner("..."):
                r = requests.post(
                    f"{base}/predict",
                    json=payload,
                    headers={"X-API-KEY": key},
                    timeout=60,
                )
            if r.status_code == 200:
                prob = r.json()["probability"]
                level_key = risk_level(prob)
                level_text = ss["levels"][level_key]
                st.subheader(level_text)
                st.write(ss["msg"].format(level=level_text.lower() if lang == "English" else level_text))
                st.caption(ss["disclaimer"])
            elif r.status_code == 401:
                st.error(ss["err_auth"])
            else:
                st.error(f"{ss['err_other']} ({r.status_code})")
        except requests.exceptions.RequestException:
            st.error(ss["err_conn"])            