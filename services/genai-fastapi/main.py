# main.py
from fastapi import FastAPI, HTTPException, File, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List
import os
import tempfile
import uuid
import traceback
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue
from openai import OpenAI
from numpy import dot
from numpy.linalg import norm
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

# ---------------- ENV/APP SETUP ----------------
load_dotenv()

app = FastAPI()
origins = ["http://localhost:3000"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# ---------------- DATABASES ----------------
mongo_client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
mongo_db = mongo_client["journal_app"]
journal_collection = mongo_db["journals"]
user_profile_collection = mongo_db["users"]

qdrant = QdrantClient(host=os.getenv("QDRANT_HOST", "localhost"), port=int(os.getenv("QDRANT_PORT", 6333)))
COLLECTION_NAME = "journal_embeddings"
if COLLECTION_NAME not in [col.name for col in qdrant.get_collections().collections]:
    qdrant.recreate_collection(collection_name=COLLECTION_NAME, vectors_config=VectorParams(size=1536, distance=Distance.COSINE))

# PostgreSQL
SQLALCHEMY_DATABASE_URL = os.getenv("POSTGRES_URL", "postgresql://postgres:password@localhost/journal_auth")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ---------------- AUTH MODELS ----------------
class User(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True, index=True)
    hashed_password = Column(String)

Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def hash_password(password: str): return pwd_context.hash(password)
def verify_password(plain, hashed): return pwd_context.verify(plain, hashed)

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    return user if user and verify_password(password, user.hashed_password) else False

def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user.username

# ---------------- REQUEST SCHEMAS ----------------
class JournalEntry(BaseModel):
    transcript: str

class EmbeddingQuery(BaseModel):
    query_text: str

class UserProfile(BaseModel):
    goals: List[str]
    principles: List[str]

class RegisterRequest(BaseModel):
    username: str
    password: str

# ---------------- ROUTES ----------------
@app.post("/register")
def register_user(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status_code=400, detail="User already exists")
    db.add(User(username=req.username, hashed_password=hash_password(req.password)))
    db.commit()
    return {"message": "User registered successfully"}

@app.post("/token")
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/setup-profile")
def setup_profile(profile: UserProfile, user_id: str = Depends(get_current_user)):
    try:
        goal_vectors = [client.embeddings.create(model="text-embedding-ada-002", input=goal).data[0].embedding for goal in profile.goals]
        principle_vectors = [client.embeddings.create(model="text-embedding-ada-002", input=p).data[0].embedding for p in profile.principles]

        user_profile_collection.update_one(
            {"_id": user_id},
            {"$set": {"goals": profile.goals, "principles": profile.principles,
                       "goal_vectors": goal_vectors, "principle_vectors": principle_vectors}},
            upsert=True
        )
        return {"message": "Profile set successfully"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Setup profile failed")

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Only audio files supported")
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        with open(tmp_path, "rb") as f:
            transcript = client.audio.transcriptions.create(model="whisper-1", file=f).text
        return {"transcript": transcript}
    finally:
        if os.path.exists(tmp_path): os.remove(tmp_path)

@app.post("/summarize")
def summarize(entry: JournalEntry, user_id: str = Depends(get_current_user)):
    try:
        response = client.chat.completions.create(model="gpt-4", messages=[
            {"role": "system", "content": "You are a motivational coach."},
            {"role": "user", "content": f"Summarize and provide feedback for: {entry.transcript}"}
        ])
        summary = response.choices[0].message.content
        embedding = client.embeddings.create(model="text-embedding-ada-002", input=entry.transcript).data[0].embedding
        entry_id = str(uuid.uuid4())
        journal_collection.insert_one({"_id": entry_id, "user_id": user_id, "transcript": entry.transcript, "summary": summary})
        qdrant.upsert(collection_name=COLLECTION_NAME, points=[PointStruct(id=entry_id, vector=embedding, payload={"user_id": user_id})])

        user = user_profile_collection.find_one({"_id": user_id})
        alignments = []
        if user:
            for goal, vec in zip(user.get("goals", []), user.get("goal_vectors", [])):
                score = dot(embedding, vec) / (norm(embedding) * norm(vec))
                if score > 0.8:
                    alignments.append(f"👍 Aligned with: {goal}")
                elif score > 0.5:
                    alignments.append(f"🔁 Partially aligned with: {goal}")
                else:
                    alignments.append(f"⚠️ Misaligned with: {goal}")

        return {"summary": summary, "goal_alignment": alignments}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Summarization failed")

@app.post("/search")
def search(query: EmbeddingQuery, user_id: str = Depends(get_current_user)):
    try:
        vec = client.embeddings.create(model="text-embedding-ada-002", input=query.query_text).data[0].embedding
        results = qdrant.search(collection_name=COLLECTION_NAME, query_vector=vec, limit=5,
            query_filter=Filter(must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]))
        ids = [r.id for r in results]
        entries = journal_collection.find({"_id": {"$in": ids}})
        return {"matches": [{"transcript": e["transcript"], "summary": e.get("summary", ""), "id": str(e["_id"])} for e in entries]}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Search failed")
