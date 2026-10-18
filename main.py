import os
import json
import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from zoneinfo import ZoneInfo

# ==========================================
# 1. إعداد مفتاح الأمان للاتصال بفايربيس بشكل آمن جداً
# ==========================================
firebase_cred_json = os.environ.get("FIREBASE_CREDENTIALS")

if firebase_cred_json:
    # إذا وجدنا المفتاح في السيرفر (Render)، نحوله من نص إلى قاموس ونستخدمه
    cred_dict = json.loads(firebase_cred_json)
    cred = credentials.Certificate(cred_dict)
else:
    # إذا كنا نعمل على الجهاز المحلي، نستخدم الملف المحمي داخل .gitignore
    cred = credentials.Certificate("firebase_credentials.json")

# تهيئة فايربيس بأمان لمنع التكرار عند إعادة تشغيل السيرفر
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

app = FastAPI()

MODEL_PATH = os.path.join(os.path.dirname(__file__), "pcos_observable_model.joblib")
_bundle = joblib.load(MODEL_PATH)
pcos_model = _bundle["model"]
MODEL_FEATURES = _bundle["features"]

# ==========================================
# 2. إعدادات حماية السيرفر بالمفتاح السري (API Key Security)
# ==========================================
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=True)

# نقرأ المفتاح من بيئة السيرفر فقط بدون أي قيمة افتراضية مكشوفة في الكود
PROJECT_API_KEY = os.getenv("PROJECT_API_KEY")

def verify_api_key(api_key: str = Security(api_key_header)):
    # 1. نتأكد أولاً أن المفتاح مضبوط في إعدادات السيرفر
    if not PROJECT_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error: API Key is missing."
        )
    # 2. نقارن المفتاح القادم من التطبيق بالمفتاح السري للسيرفر
    if api_key != PROJECT_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return api_key

# ==========================================
# 3. تصميم قالب البيانات الشامل (Data Dictionary)
# ==========================================
class StudentData(BaseModel):
    participant_code: str
    age: int
    consent_given: bool          # موافقة الطالبة (مهم جداً أخلاقياً وقانونياً)
    has_pmos: bool               # هل لديها متلازمة PMOS؟
    productivity_score: int      # تقييم الإنتاجية الأكاديمية (من 1 إلى 10)
    sleep_hours: float           # ساعات النوم (رقم بفاصلة عشرية)
    fatigue_level: int           # مستوى الإرهاق (من 1 إلى 5)
    mood_status: str             # الحالة المزاجية (نص)
    stress_level: int            # مستوى التوتر
    study_hours: float           # ساعات الدراسة
    focus_level: int             # مستوى التركيز
    dietary_habits: str          # العادات الغذائية
    exercised_today: bool        # هل مارست الرياضة؟ (نعم/لا)
    exercise_duration: int       # مدة الرياضة بالدقائق


class SymptomInput(BaseModel):
    age: int
    weight_kg: float
    height_cm: float
    cycle_regular: bool          # True = منتظمة، False = غير منتظمة
    cycle_length_days: int
    weight_gain: bool
    hair_growth: bool
    skin_darkening: bool
    hair_loss: bool
    pimples: bool
    fast_food: bool
    regular_exercise: bool


# ==========================================
# 4. نقاط النهاية (Endpoints)
# ==========================================

# الباب الرئيسي
@app.get("/")
def read_root():
    return {"message": "مرحباً! السيرفر يعمل وتم الربط بقاعدة بيانات فايربيس بنجاح."}



# باب استقبال البيانات (محمي بالمفتاح السري)
@app.post("/add_student")
def add_student(data: StudentData, api_key: str = Security(verify_api_key)):
    today = datetime.now(ZoneInfo("Europe/Istanbul")).strftime("%Y-%m-%d")

    student_ref = db.collection("students").document(data.participant_code)

    # الوثيقة الرئيسية: بيانات ثابتة عن المشاركة
    student_ref.set({
        "participant_code": data.participant_code,
        "age": data.age,
        "consent_given": data.consent_given,
        "has_pmos": data.has_pmos,
    }, merge=True)

    # سجل اليوم: كل الحقول مع التاريخ ووقت الإرسال
    entry = data.model_dump()
    entry["date"] = today
    entry["submitted_at"] = firestore.SERVER_TIMESTAMP
    student_ref.collection("entries").document(today).set(entry)

    return {"message": "تم حفظ بيانات الطالبة بنجاح!", "date": today}



# نبض السيرفر لمنع السبات (Keep-Alive Endpoint)
@app.get("/ping")
def ping_server():
    return {"status": "I am awake!"}



# باب جلب البيانات للوحة التحكم (النسخة الوحيدة المحمية بالمفتاح السري)
@app.get("/get_students")
def get_students(api_key: str = Security(verify_api_key)):
    docs = db.collection_group("entries").stream()
    students_list = [doc.to_dict() for doc in docs]
    return {"data": students_list}



@app.post("/predict")
def predict(data: SymptomInput, api_key: str = Security(verify_api_key)):
    if data.height_cm <= 0:
        raise HTTPException(status_code=422, detail="height_cm must be positive")

    bmi = data.weight_kg / ((data.height_cm / 100) ** 2)

    # في بيانات Kaggle: Cycle(R/I) القيمة 2 = منتظمة، 4 = غير منتظمة
    row = {
        "Age (yrs)": data.age,
        "Weight (Kg)": data.weight_kg,
        "Height(Cm)": data.height_cm,
        "BMI": bmi,
        "Cycle(R/I)": 2 if data.cycle_regular else 4,
        "Cycle length(days)": data.cycle_length_days,
        "Weight gain(Y/N)": int(data.weight_gain),
        "hair growth(Y/N)": int(data.hair_growth),
        "Skin darkening (Y/N)": int(data.skin_darkening),
        "Hair loss(Y/N)": int(data.hair_loss),
        "Pimples(Y/N)": int(data.pimples),
        "Fast food (Y/N)": int(data.fast_food),
        "Reg.Exercise(Y/N)": int(data.regular_exercise),
    }

    X = pd.DataFrame([row])[MODEL_FEATURES]
    probability = float(pcos_model.predict_proba(X)[0][1])

    return {
        "probability": round(probability, 3),
        "risk_level": risk_level(probability),
        "disclaimer": "Research prototype only. Not a medical diagnosis."
    }

def risk_level(p):
    if p < 0.35:
        return "low"
    elif p < 0.65:
        return "moderate"
    return "high"