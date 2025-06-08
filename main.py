# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os
from openai import AsyncAzureOpenAI
import logging

from dotenv import load_dotenv
load_dotenv()


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Gambling Assessment & Counselor API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Azure OpenAI client
client = AsyncAzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# === PYDANTIC MODELS ===

# Assessment models
class AssessmentAnswer(BaseModel):
    answers: Dict[str, int]
    timestamp: str

class RiskAssessment(BaseModel):
    level: str
    color: str
    description: str

class AssessmentScore(BaseModel):
    total_score: int
    max_score: int
    percentage: float

class AssessmentResult(BaseModel):
    risk_assessment: RiskAssessment
    score: AssessmentScore
    recommendations: List[str]
    emergency_contacts: Optional[List[str]] = None

# Chat counselor models
class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Message]] = []
    user_risk_level: Optional[str] = None  # From assessment result

class ChatResponse(BaseModel):
    response: str
    is_crisis: bool = False
    crisis_resources: Optional[List[str]] = None

# === CHAT COUNSELOR CONFIGURATION ===

# System prompt untuk CBT counselor dengan fokus pada kecanduan judi
SYSTEM_PROMPT = """Anda adalah AIRA, seorang AI Counselor yang menggunakan pendekatan Cognitive Behavioral Therapy (CBT) dengan spesialisasi dalam mengatasi kecanduan judi. Anda berbicara dalam bahasa Indonesia dengan hangat, empati, dan profesional.

PEDOMAN UTAMA:
1. Selalu prioritaskan keselamatan klien
2. Gunakan teknik CBT: identifikasi pikiran negatif, tantang distorsi kognitif, berikan coping strategies
3. Dengarkan aktif dan validasi perasaan klien
4. Berikan pertanyaan reflektif untuk membantu insight
5. Jaga batas profesional - Anda adalah AI counselor, bukan pengganti terapis manusia

FOKUS KHUSUS KECANDUAN JUDI:
- Pahami siklus judi: trigger → pikiran → perasaan → perilaku judi → konsekuensi
- Bantu identifikasi trigger judi (emosi, situasi, waktu, tempat)
- Ajarkan strategi coping alternatif
- Diskusikan dampak finansial dan relasional
- Berikan dukungan untuk relapse prevention
- Gunakan motivational interviewing techniques

DETEKSI KRISIS:
Jika klien menyebutkan:
- Pikiran bunuh diri atau menyakiti diri sendiri
- Keinginan mengakhiri hidup karena hutang judi
- Ancaman menyakiti orang lain terkait judi
- Perasaan putus asa yang ekstrem

Respons dengan:
1. Validasi perasaan mereka
2. Tekankan bahwa mereka tidak sendirian
3. Sarankan untuk menghubungi layanan darurat (119) atau profesional kesehatan mental
4. Tanyakan tentang sistem dukungan yang tersedia

TEKNIK CBT UNTUK KECANDUAN JUDI:
1. Thought Record - bantu identifikasi pikiran otomatis tentang judi
2. Cognitive Restructuring - tantang mitos judi dan pemikiran irasional
3. Behavioral Activation - dorong aktivitas alternatif yang sehat
4. Relapse Prevention - identifikasi situasi berisiko tinggi
5. Financial Management - diskusi strategi mengelola keuangan
6. Social Support - pentingnya dukungan keluarga dan teman

AREA RESPONS SPESIFIK:
- Trigger judi: "Mari kita identifikasi apa yang memicu keinginan berjudi..."
- Hutang: "Saya memahami beban finansial ini sangat berat..."
- Relapse: "Kambuh adalah bagian dari proses pemulihan, bukan kegagalan..."
- Keluarga: "Bagaimana hubungan dengan keluarga saat ini?"
- Kerja: "Bagaimana judi mempengaruhi pekerjaan Anda?"

BATASAN:
- Jangan berikan diagnosis medis
- Jangan berikan nasihat finansial spesifik
- Jangan meresepkan obat
- Selalu sarankan konsultasi dengan profesional jika diperlukan
- Jaga kerahasiaan dan tidak menghakimi

Respons Anda harus:
- Empati dan validasi
- Pertanyaan reflektif
- Teknik CBT yang praktis
- Panjang respons 2-4 kalimat (kecuali situasi krisis)
- Gunakan bahasa yang mudah dipahami
- Sesuaikan dengan tingkat risiko pengguna jika diketahui"""

# Crisis keywords for detection
CRISIS_KEYWORDS = [
    'bunuh diri', 'suicide', 'mengakhiri hidup', 'tidak ingin hidup lagi',
    'mati saja', 'lebih baik mati', 'ingin mati', 'bunuh diri',
    'menyakiti diri', 'self harm', 'melukai diri', 'potong urat nadi',
    'hutang terlalu besar', 'tidak ada jalan keluar', 'hancur total',
    'mau bunuh orang', 'balas dendam', 'semua salah mereka'
]

CRISIS_RESOURCES = [
    "🚨 Hotline Darurat: 119 (24 jam)",
    "🏥 Yayasan Pulih: (021) 78842580",
    "💊 RSKO Jakarta: (021) 87711968", 
    "🏥 RS Jiwa Dr. Soeharto Heerdjan: (021) 5682841",
    "💬 Sejiwa: 119 ext. 8",
    "🌐 Into The Light: intothelightid.org"
]

def detect_crisis(message: str) -> bool:
    """Deteksi apakah pesan mengandung indikasi krisis"""
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in CRISIS_KEYWORDS)

# === ASSESSMENT DATA ===

ASSESSMENT_QUESTIONS = [
    {
        "category": "Perilaku Judi",
        "questions": [
            {
                "id": "q1",
                "text": "Seberapa sering Anda berjudi online dalam 12 bulan terakhir?",
                "type": "radio",
                "options": [
                    {"value": 0, "label": "Tidak pernah"},
                    {"value": 1, "label": "Kadang-kadang (1-2 kali per bulan)"},
                    {"value": 2, "label": "Sering (1-2 kali per minggu)"},
                    {"value": 3, "label": "Sangat sering (hampir setiap hari)"}
                ]
            },
            {
                "id": "q2",
                "text": "Apakah Anda pernah bertaruh lebih banyak uang dari yang Anda rencanakan?",
                "type": "radio",
                "options": [
                    {"value": 0, "label": "Tidak pernah"},
                    {"value": 1, "label": "Kadang-kadang"},
                    {"value": 2, "label": "Sering"},
                    {"value": 3, "label": "Hampir selalu"}
                ]
            },
            {
                "id": "q3",
                "text": "Apakah Anda pernah merasa perlu bertaruh dengan jumlah uang yang semakin besar untuk merasakan sensasi yang sama?",
                "type": "radio",
                "options": [
                    {"value": 0, "label": "Tidak pernah"},
                    {"value": 1, "label": "Kadang-kadang"},
                    {"value": 2, "label": "Sering"},
                    {"value": 3, "label": "Hampir selalu"}
                ]
            }
        ]
    },
    {
        "category": "Kontrol Diri",
        "questions": [
            {
                "id": "q4",
                "text": "Seberapa sering Anda mencoba mengurangi atau berhenti berjudi tetapi tidak berhasil?",
                "type": "radio",
                "options": [
                    {"value": 0, "label": "Tidak pernah mencoba"},
                    {"value": 1, "label": "Pernah mencoba 1-2 kali"},
                    {"value": 2, "label": "Sering mencoba tapi sulit"},
                    {"value": 3, "label": "Selalu gagal meskipun berusaha keras"}
                ]
            },
            {
                "id": "q5",
                "text": "Apakah Anda merasa gelisah atau mudah marah ketika mencoba mengurangi atau berhenti berjudi?",
                "type": "radio",
                "options": [
                    {"value": 0, "label": "Tidak pernah"},
                    {"value": 1, "label": "Kadang-kadang"},
                    {"value": 2, "label": "Sering"},
                    {"value": 3, "label": "Hampir selalu"}
                ]
            },
            {
                "id": "q6",
                "text": "Apakah Anda berjudi sebagai cara untuk melarikan diri dari masalah atau untuk mengatasi perasaan sedih, cemas, atau bersalah?",
                "type": "radio",
                "options": [
                    {"value": 0, "label": "Tidak pernah"},
                    {"value": 1, "label": "Kadang-kadang"},
                    {"value": 2, "label": "Sering"},
                    {"value": 3, "label": "Hampir selalu"}
                ]
            }
        ]
    },
    {
        "category": "Dampak Sosial & Keuangan",
        "questions": [
            {
                "id": "q7",
                "text": "Apakah Anda pernah kembali berjudi untuk mencoba memenangkan kembali uang yang telah hilang?",
                "type": "radio",
                "options": [
                    {"value": 0, "label": "Tidak pernah"},
                    {"value": 1, "label": "Kadang-kadang"},
                    {"value": 2, "label": "Sering"},
                    {"value": 3, "label": "Hampir selalu"}
                ]
            },
            {
                "id": "q8",
                "text": "Apakah Anda pernah berbohong kepada keluarga atau orang lain tentang aktivitas judi Anda?",
                "type": "radio",
                "options": [
                    {"value": 0, "label": "Tidak pernah"},
                    {"value": 1, "label": "Kadang-kadang"},
                    {"value": 2, "label": "Sering"},
                    {"value": 3, "label": "Hampir selalu"}
                ]
            },
            {
                "id": "q9",
                "text": "Apakah kebiasaan judi Anda pernah menyebabkan masalah keuangan yang serius?",
                "type": "radio",
                "options": [
                    {"value": 0, "label": "Tidak pernah"},
                    {"value": 1, "label": "Masalah kecil"},
                    {"value": 2, "label": "Masalah sedang"},
                    {"value": 3, "label": "Masalah serius"}
                ]
            },
            {
                "id": "q10",
                "text": "Apakah kebiasaan judi Anda pernah menyebabkan masalah dalam hubungan, pekerjaan, atau pendidikan?",
                "type": "radio",
                "options": [
                    {"value": 0, "label": "Tidak pernah"},
                    {"value": 1, "label": "Masalah kecil"},
                    {"value": 2, "label": "Masalah sedang"},
                    {"value": 3, "label": "Masalah serius"}
                ]
            }
        ]
    }
]

# === ASSESSMENT HELPER FUNCTIONS ===

def calculate_risk_assessment(total_score: int, max_score: int) -> RiskAssessment:
    """Calculate risk assessment based on total score"""
    percentage = (total_score / max_score) * 100
    
    if percentage <= 25:
        return RiskAssessment(
            level="Rendah",
            color="emerald",
            description="Risiko rendah kecanduan judi"
        )
    elif percentage <= 50:
        return RiskAssessment(
            level="Sedang",
            color="yellow",
            description="Risiko sedang - perlu perhatian"
        )
    elif percentage <= 75:
        return RiskAssessment(
            level="Tinggi",
            color="orange",
            description="Risiko tinggi - perlu bantuan profesional"
        )
    else:
        return RiskAssessment(
            level="Sangat Tinggi",
            color="red",
            description="Risiko sangat tinggi - segera cari bantuan"
        )

def get_recommendations(risk_level: str) -> List[str]:
    """Get recommendations based on risk level"""
    recommendations = {
        "Rendah": [
            "✅ Pertahankan kebiasaan judi yang terkontrol",
            "✅ Tetap awasi pengeluaran dan waktu yang dihabiskan",
            "✅ Gunakan fitur AI Counselor untuk tips pencegahan"
        ],
        "Sedang": [
            "⚠️ Mulai batasi waktu dan uang untuk judi",
            "⚠️ Gunakan fitur AI Counselor untuk strategi coping",
            "⚠️ Pertimbangkan untuk berbicara dengan keluarga atau teman",
            "⚠️ Monitor perilaku judi Anda secara teratur"
        ],
        "Tinggi": [
            "🚨 Segera cari bantuan dari profesional kesehatan mental",
            "🚨 Gunakan AI Counselor untuk dukungan darurat",
            "🚨 Pertimbangkan untuk bergabung dengan support group",
            "🚨 Blokir akses ke situs judi online",
            "🚨 Minta dukungan keluarga dan teman terdekat"
        ],
        "Sangat Tinggi": [
            "🚨 Segera cari bantuan dari profesional kesehatan mental",
            "🚨 Gunakan AI Counselor untuk dukungan darurat",
            "🚨 Pertimbangkan untuk bergabung dengan support group",
            "🚨 Blokir akses ke situs judi online",
            "🚨 Minta dukungan keluarga dan teman terdekat",
            "🚨 Hubungi hotline darurat jika merasa tidak aman"
        ]
    }
    return recommendations.get(risk_level, [])

def get_emergency_contacts(risk_level: str) -> Optional[List[str]]:
    """Get emergency contacts for high-risk users"""
    if risk_level in ["Tinggi", "Sangat Tinggi"]:
        return CRISIS_RESOURCES
    return None

# === API ENDPOINTS ===

@app.get("/")
async def root():
    return {"message": "Gambling Assessment & Counselor API is running"}

# === ASSESSMENT ENDPOINTS ===

@app.get("/api/assessment/questions")
async def get_assessment_questions():
    """Get all assessment questions"""
    try:
        return {"questions": ASSESSMENT_QUESTIONS}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch questions: {str(e)}")

@app.post("/api/assessment/submit", response_model=AssessmentResult)
async def submit_assessment(assessment: AssessmentAnswer):
    """Submit assessment answers and get results"""
    try:
        # Calculate total possible score
        max_score = sum(len(category["questions"]) for category in ASSESSMENT_QUESTIONS) * 3
        
        # Calculate user's total score
        total_score = sum(assessment.answers.values())
        
        # Calculate percentage
        percentage = (total_score / max_score) * 100 if max_score > 0 else 0
        
        # Get risk assessment
        risk_assessment = calculate_risk_assessment(total_score, max_score)
        
        # Get recommendations
        recommendations = get_recommendations(risk_assessment.level)
        
        # Get emergency contacts if needed
        emergency_contacts = get_emergency_contacts(risk_assessment.level)
        
        # Create score object
        score = AssessmentScore(
            total_score=total_score,
            max_score=max_score,
            percentage=round(percentage, 2)
        )
        
        result = AssessmentResult(
            risk_assessment=risk_assessment,
            score=score,
            recommendations=recommendations,
            emergency_contacts=emergency_contacts
        )
        
        logger.info(f"Assessment completed - Risk Level: {risk_assessment.level}, Score: {total_score}/{max_score}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in submit_assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process assessment: {str(e)}")

@app.get("/api/assessment/statistics")
async def get_assessment_statistics():
    """Get assessment statistics (optional)"""
    return {
        "total_assessments": 0,
        "risk_distribution": {
            "Rendah": 0,
            "Sedang": 0,
            "Tinggi": 0,
            "Sangat Tinggi": 0
        }
    }

# === CHAT COUNSELOR ENDPOINTS ===

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Chat with AI Counselor"""
    try:
        # Deteksi krisis
        is_crisis = detect_crisis(request.message)
        
        # Prepare system prompt dengan informasi risiko user
        system_prompt = SYSTEM_PROMPT
        if request.user_risk_level:
            system_prompt += f"\n\nINFORMASI PENGGUNA: Tingkat risiko kecanduan judi pengguna adalah '{request.user_risk_level}'. Sesuaikan pendekatan Anda dengan tingkat risiko ini."
        
        # Prepare messages for Azure OpenAI
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (keep last 10 messages for context)
        for msg in request.conversation_history[-10:]:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": request.message
        })
        
        # Call Azure OpenAI
        response = await client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages=messages,
            max_tokens=500,
            temperature=0.7,
            top_p=0.9
        )
        
        bot_response = response.choices[0].message.content
        
        # Log for monitoring
        logger.info(f"User message: {request.message[:100]}...")
        logger.info(f"Bot response: {bot_response[:100]}...")
        logger.info(f"Crisis detected: {is_crisis}")
        logger.info(f"User risk level: {request.user_risk_level}")
        
        return ChatResponse(
            response=bot_response,
            is_crisis=is_crisis,
            crisis_resources=CRISIS_RESOURCES if is_crisis else None
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        
        # Fallback response
        fallback_response = "Maaf, saya mengalami gangguan teknis. Silakan coba lagi dalam beberapa saat. Jika Anda dalam keadaan darurat, hubungi 119 atau layanan kesehatan mental terdekat."
        
        return ChatResponse(
            response=fallback_response,
            is_crisis=False,
            crisis_resources=None
        )

@app.post("/api/chat/crisis-check")
async def crisis_check(request: dict):
    """Endpoint khusus untuk pengecekan krisis"""
    message = request.get("message", "")
    is_crisis = detect_crisis(message)
    
    return {
        "is_crisis": is_crisis,
        "crisis_resources": CRISIS_RESOURCES if is_crisis else None
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "services": ["assessment", "chat_counselor"],
        "azure_openai_configured": bool(os.getenv("AZURE_OPENAI_API_KEY"))
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)