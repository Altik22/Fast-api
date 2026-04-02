from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔑 ключи
SUPABASE_URL = "https://poxydnxojhvbssxlnvrv.supabase.co"
SUPABASE_KEY = "sb_publishable_mbz3m1lisF4tHcn1CrXJ6Q_S5Q9F-5W"
GEMINI_KEY = "AIzaSyBu0Wp4sxXyUO_O1utvxNQ5nMd8TlzFlrs"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-pro")

class UserData(BaseModel):
    name: str
    score: int
    subject: str

@app.post("/recommend")
async def recommend(data: UserData):
    
    # 📦 берем универы из базы
    response = supabase.table("universities").select("*").execute()
    universities = response.data

    # 📊 фильтр по баллам
    filtered = [u for u in universities if u["min_score"] <= data.score]

    # 🤖 отправка в Gemini
    prompt = f"""
    Студент: {data.name}
    Балл: {data.score}
    Предмет: {data.subject}

    Вот список университетов:
    {filtered}

    Дай лучший совет и список подходящих вузов
    """

    ai_response = model.generate_content(prompt)

    return {"answer": ai_response.text}

@app.get("/universities")
async def get_universities():
    try:
        # Query the 'universities' table
        # .select("*") fetches all columns; you can replace "*" with "id, name" for specific ones
        response = supabase.table("universitets").select("*").execute()
        
        # The data is located in the .data attribute of the response
        return response.data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))