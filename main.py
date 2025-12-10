from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from openai.error import RateLimitError, OpenAIError
import os

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI Client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.get("/")
def home():
    return {"message": "Gold Bot is running. Use /predict endpoint."}

@app.get("/predict")
def predict(price: float):

    prompt = f"""
    Gold price now = {price}.
    Give short forecast: uptrend or downtrend and expected short move.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        forecast = response.choices[0].message["content"]

    except RateLimitError:
        forecast = "AI forecast unavailable: quota exceeded."

    except OpenAIError as e:
        forecast = f"AI forecast failed: {str(e)}"

    except Exception as e:
        forecast = f"Unexpected error: {str(e)}"

    return {"price": price, "forecast": forecast}