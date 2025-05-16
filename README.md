# 🧠 Journal Coach App

A personal journaling app that transcribes your audio entries, summarizes them, and gives motivational feedback. Supports goal alignment using vector search and semantic embeddings.

---

## 📁 Project Structure

```
journal-app/
├── frontend/              # React frontend (user interface)
├── services/genai-fastapi/  # FastAPI backend (API, auth, OpenAI integration)
├── .gitignore
├── README.md
└── ...
```

---

## ⚙️ Requirements

- Node.js (v18+)
- Python (3.10+ recommended)
- MongoDB
- PostgreSQL
- Qdrant (Vector DB)
- OpenAI API Key

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/journal-app.git
cd journal-app
```

---

### 2. Set Up the Backend (FastAPI)

```bash
cd services/genai-fastapi
python -m venv venv
venv\Scripts\activate  # or source venv/bin/activate on Mac/Linux

pip install -r requirements.txt
```

#### 📄 Create `.env` file

```env
OPENAI_API_KEY=your-openai-key
MONGO_URI=mongodb://localhost:27017/
POSTGRES_URL=postgresql://postgres:password@localhost/journal_auth
SECRET_KEY=your_jwt_secret
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

#### Run FastAPI server:

```bash
uvicorn main:app --reload
```

FastAPI will be running at: [http://localhost:8000](http://localhost:8000)

---

### 3. Set Up the Frontend (React)

```bash
cd ../../frontend
npm install
npm start
```

Frontend will run at: [http://localhost:3000](http://localhost:3000)

---

## 🔐 Authentication

The app uses OAuth2 + JWT:

- Register via `/register`
- Login via `/token`
- Store your token in the frontend to access authenticated routes

---

## ✨ Features

- 🎤 Audio Transcription (Whisper API)
- 🧠 Smart Summarization + Feedback (GPT-4)
- 🎯 Goal Alignment Check (Qdrant + cosine similarity)
- 🔎 Semantic Search over your journal entries
- 👤 User Profiles with long-term goals and principles
- 🛡️ Secure JWT-based Auth

---

## 🧪 Example API Routes

- `POST /register` – Register a user
- `POST /token` – Login and receive JWT
- `POST /transcribe` – Upload audio, get transcript
- `POST /summarize` – Get feedback + goal alignment
- `POST /search` – Find similar past entries

---

## 🛠️ Tech Stack

- 🧪 **FastAPI** + **SQLAlchemy** + **MongoDB**
- ⚛️ **React** + **Vite** + **JWT Auth**
- 💬 **OpenAI Whisper + GPT-4**
- 🧠 **Qdrant** for vector search

---

## 🤝 Contributing

PRs welcome! Please create feature branches off `development`.
