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
        r = requests.get(GOLD_API, timeout=10)
        r.raise_for_status()
        data = r.json()
        # Metals.live format check
        if len(data) > 0 and "gold" in data[0]:
            return data[0]["gold"]
        else:
            return 1950.00  # fallback value
    except Exception:
        return 1950.00  # fallback value if API fails

# ---------- Root Endpoint (Optional) ----------
@app.get("/")
def root():
    return {"message": "Gold Bot is running. Use /predict endpoint."}

# ---------- Predict Endpoint ----------
@app.get("/predict")
def predict():
    price = get_gold_price()

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