import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, firestore

# 1. إعداد مفتاح الأمان للاتصال بفايربيس بشكل آمن جداً
# نحاول جلب المفتاح السري من بيئة السيرفر (Render)
firebase_cred_json = os.environ.get("FIREBASE_CREDENTIALS")

if firebase_cred_json:
    # إذا وجدنا المفتاح في السيرفر، نحوله من نص إلى قاموس (Dictionary) ونستخدمه
    cred_dict = json.loads(firebase_cred_json)
    cred = credentials.Certificate(cred_dict)
else:
    # إذا لم نجده (أي أننا نعمل على جهازك المحلي)، نستخدم الملف العادي
    # (تأكدنا مسبقاً أن هذا الملف محمي داخل .gitignore)
    cred = credentials.Certificate("serviceAccountKey.json")

# تهيئة فايربيس (نتأكد أولاً أنه لم يتم تهيئته مسبقاً لتجنب الأخطاء عند إعادة تشغيل السيرفر)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

app = FastAPI()

# ... (باقي الكود يبقى كما هو أسفل هذا السطر بدءاً من class StudentData)

# 2. تصميم قالب البيانات الشامل (Data Dictionary)
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

# 3. الباب الرئيسي
@app.get("/")
def read_root():
    return {"message": "مرحباً! السيرفر يعمل وتم الربط بقاعدة بيانات فايربيس بنجاح."}

# 4. باب استقبال البيانات
@app.post("/add_student")
def add_student(data: StudentData):
    # التعديل هنا: استخدمنا participant_code بدلاً من student_id الذي كان يسبب انهيار السيرفر
    doc_ref = db.collection("students").document(data.participant_code)
    
    # تحويل البيانات المعتمدة من حارس الأمن إلى صيغة تفهمها قاعدة البيانات وحفظها
    doc_ref.set(data.model_dump()) 
    
    return {"message": "تم حفظ بيانات الطالبة بنجاح!", "saved_data": data}

    # 5. باب جلب البيانات للوحة التحكم
@app.get("/get_students")
def get_students():
    docs = db.collection("students").stream()
    # تحويل البيانات المسحوبة إلى قائمة (List)
    students_list = [doc.to_dict() for doc in docs]
    return {"data": students_list}