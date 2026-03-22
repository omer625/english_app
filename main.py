import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import google.generativeai as genai

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Gemini API Yapılandırması
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
# Model tanımlamasını buraya ekledik (Hata almamak için şart)
model = genai.GenerativeModel('gemini-1.5-flash')

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Ana sayfayı yükleyen GET isteği
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ask-gemini")
async def ask_gemini(task: str = Form(...), level: str = Form(...), user_input: str = Form("")):
    """
    Tüm AI isteklerini yöneten ana fonksiyon.
    """
    prompts = {
        "quiz": f"Bana {level} seviyesinde İngilizce bir kelime sorusu sor. Çoktan seçmeli olsun (A, B, C, D). Sadece soruyu ve şıkları yaz, cevabı en sonda 'Cevap: [Şık]' şeklinde belirt.",
        "grammar": f"Bana {level} seviyesinde bir İngilizce gramer boşluk doldurma sorusu sor. Kullanıcının cümleyi tamamlamasını iste.",
        "analysis": f"Şu İngilizce cümleyi analiz et: '{user_input}'. Hataları Türkçe açıkla, gramer kurallarını belirt ve doğrusunu göster."
    }
    
    try:
        # Seçilen göreve göre Gemini'den yanıt alıyoruz
        response = model.generate_content(prompts.get(task, "Merhaba"))
        # Yanıtı string olarak sözlük içinde dönüyoruz
        return {"result": str(response.text)}
    except Exception as e:
        return {"result": f"Hata oluştu: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    # Railway'in verdiği portu kullan, yoksa 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
