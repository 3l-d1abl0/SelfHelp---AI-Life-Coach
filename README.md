# 🧘 SelfHelp 🧘- AI Life Coach / Mentor  

🚀 **Unlock Your Potential with a Personalized AI Life Coach**  
An interactive platform where users engage in empathetic, voice-driven conversations with an AI mentor for emotional support, personal growth, and holistic life balance.
AI Life Coach is a personalized, emotionally intelligent virtual mentor designed to guide users through self-growth, emotional challenges, and life decisions.

This AI-powered platform combines real-time speech transcription, intelligent dialog generation, and a virtual avatar to simulate a deeply human coaching experience.

---

## 🎯 **Key Features**  
- **Real-time Voice-Driven Conversations**: Speak naturally to your AI mentor, with real-time transcription via AssemblyAI.  
- **Emotionally Intelligent Responses**: Powered by **Google Gemini**, tuned for personal growth, empathy, and insight.
- **Virtual Avatar Guidance**: The AI mentor is visually represented using HeyGen avatars with real-time lip-sync and voice.  
- **Progress Reflection**: Track conversations and insights (stored in MongoDB) for self-discovery.  
- **Holistic Support**: Get tailored advice on career, relationships, and wellness.  

---

## 🔧 **Tech Stack**  
| Category       | Technology       | Use Case                          |  
|----------------|------------------|-----------------------------------|  
| **Frontend**   | Svelte           | Responsive, interactive UI        |  
| **Backend**    | FastAPI          | REST APIs for AI logic & data flow|  
| **AI Model**   | Google Gemini    | Empathetic life coaching responses|  
| **Database**   | MongoDB + Redis  | User data & conversation storage  |  
| **Transcription** | AssemblyAI   | Real-time speech-to-text          |  
| **Avatar**     | HeyGen           | Virtual AI mentor presence        |  

---

## 🛠️ **Setup & Installation**  
1. **Clone the repo**:  
   ```bash  
   git clone https://github.com/3l-d1abl0/SelfHelp---AI-Life-Coach.git
   cd ai-life-coach  

    Backend (FastAPI):

    cd SelfHelp-server
    pip install -r requirements.txt  
    python3 src/run.py 

    Frontend (Svelte):
    
    cd cd SelfHelp-frontend
    npm install  
    npm run dev  

Environment Variables:
Create .env files for backend/ with:
env

    # Backend .env  
    GEMINI_API_KEY=your_google_api_key  
    ASSEMBLYAI_API_KEY=your_assemblyai_key  
    HEYGEN_API_KEY=your_heygen_key  
    MONGO_URI=your_mongodb_uri  
    REDIS_URL=your_redis_url  


📂 Project Structure


ai-life-coach/
├── SelfHelp-server/  # FastAPI server  
│   ├── envs/            
│   ├── requirements.txt
│   ├── src
│   │   ├── app
│   │   │   ├── api/    # Core API routes 
│   │   │   ├── config.py
│   │   │   ├── db/
│   │   │   ├── lib/
│   │   │   ├── logger.py
│   │   │   ├── main.py
│   │   │   ├── middleware.py
│   │   │   ├── models/
│   │   ├── logs
│   │   │   └── app.log
│   │   └── run.py
│   └── tests
│       └── test_websocket.py
├── SelfHelp-frontend/              # Svelte app  
│   ├── src/  
│   │   └── routes/        
└── README.md  

