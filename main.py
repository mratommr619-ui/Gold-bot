from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os
import requests

app = FastAPI()

# ---------- CORS Middleware ----------
# Frontend / Acode preview / Browser fetch အတွက်
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # အားလုံး allow
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- OpenAI API Key ----------
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise Exception("OPENAI_API_KEY environment variable not set")

client = OpenAI(api_key=openai_api_key)

# ---------- Gold Price Fetch Function ----------
GOLD_API = "https://api.metals.live/v1/spot"

def get_gold_price():
    try:
        r = requests.get(GOLD_API, timeout=5)
        r.raise_for_status()
        return r.json()[0]["gold"]
    except Exception:
        return None

# ---------- Root Endpoint (Optional) ----------
@app.get("/")
def root():
    return {"message": "Gold Bot is running. Use /predict endpoint."}

# ---------- Predict Endpoint ----------
@app.get("/predict")
def predict():
    price = get_gold_price()
    if not price:
        return {"error": "Failed to fetch gold price"}

    # Prompt for OpenAI
    prompt = f"""
    You are a financial bot.
    Current gold price: {price}
    Provide:
    - Short-term prediction
    - Trend direction
    - Support & resistance
    - Risk note
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    forecast = response.choices[0].message["content"]

    return {
        "price": price,
        "forecast": forecast
    }