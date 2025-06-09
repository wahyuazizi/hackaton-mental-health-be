from typing import List, Dict, Any

# Assessment Questions Data
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

# Crisis Detection
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

# CBT System Prompt
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
