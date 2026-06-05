import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "study-data-ikanx101-super-secret-key-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./study_data.db")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB

SECURITY_QUESTIONS = [
    "Apa nama hewan peliharaan pertama kamu?",
    "Apa nama kota kelahiran ibumu?",
    "Apa makanan favorit kamu?",
    "Apa judul lagu favorit kamu?",
    "Apa merek HP pertama kamu?",
    "Apa nama sekolah dasar kamu?",
    "Apa nama jalan tempat kamu tumbuh besar?",
]
