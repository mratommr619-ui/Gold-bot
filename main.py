from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI, error as openai_error
import os
import requests

app = FastAPI()

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- OpenAI Client ----------
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    client = OpenAI(api_key=openai_api_key)
else:
    client = None
    print("WARNING: OPENAI_API_KEY not set. AI forecast fallback only.")

# ---------- Gold Price Fetch ----------
GOLD_API = "https://api.metals.live/v1/spot"

def get_gold_price():
    try:
        r = requests.get(GOLD_API, timeout=10)
        r.raise_for_status()
        data = r.json()
        if len(data) > 0 and "gold" in data[0]:
            return data[0]["gold"]
        else:
            return 1950.0
    except Exception:
        return 1950.0

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
        except openai_error.RateLimitError:
            forecast = "AI forecast unavailable: quota exceeded. Try again later."
        except Exception as e:
            forecast = f"AI forecast failed: {str(e)}"
    else:
        forecast = "AI forecast unavailable: OPENAI_API_KEY not set."

    return {
        "price": price,
        "forecast": forecast
    }