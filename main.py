import os
from pathlib import Path
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from groq import Groq

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Groq istemcisi
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/ask-gemini")
async def ask_gemini(task: str = Form(...), level: str = Form(...), user_input: str = Form("")):
    prompts = {
        "quiz": f"Bana {level} seviyesinde İngilizce bir kelime sorusu sor. Çoktan seçmeli olsun (A, B, C, D). Sadece soruyu ve şıkları yaz, cevabı en sonda 'Cevap: [Şık]' şeklinde belirt.",
        "grammar": f"Bana {level} seviyesinde bir İngilizce gramer boşluk doldurma sorusu sor.",
        "analysis": f"Şu İngilizce cümleyi analiz et: '{user_input}'. Hataları Türkçe açıkla ve doğrusunu göster."
    }

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompts.get(task, "Hello")}]
        )
        return JSONResponse(content={"result": response.choices[0].message.content})
    except Exception as e:
        return JSONResponse(content={"result": f"Hata: {str(e)}"})

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
