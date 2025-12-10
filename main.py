from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os
import requests

app = FastAPI()

# ---------- CORS Middleware ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # All origins allowed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- OpenAI API Key ----------
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("WARNING: OPENAI_API_KEY not set. AI forecast will fallback.")
client = OpenAI(api_key=openai_api_key) if openai_api_key else None

# ---------- Gold Price Fetch Function ----------
GOLD_API = "https://api.metals.live/v1/spot"

def get_gold_price():
    try:
        r = requests.get(GOLD_API, timeout=10)
        r.raise_for_status()
        data = r.json()
        if len(data) > 0 and "gold" in data[0]:
            return data[0]["gold"]
        else:
            return 1950.00  # fallback
    except Exception:
        return 1950.00  # fallback

# ---------- Root Endpoint ----------
@app.get("/")
def root():
    return {"message": "Gold Bot is running. Use /predict endpoint."}

# ---------- Predict Endpoint ----------
@app.get("/predict")
def predict():
    price = get_gold_price()

    prompt = f"""
    You are a financial bot.
    Current gold price: {price}
    Provide:
    - Short-term prediction
    - Trend direction
    - Support & resistance
    - Risk note
    """

    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            forecast = response.choices[0].message["content"]
        except Exception as e:
            forecast = f"AI forecast failed: {str(e)}"
    else:
        forecast = "AI forecast not available. Set OPENAI_API_KEY."

    return {
        "price": price,
        "forecast": forecast
    }