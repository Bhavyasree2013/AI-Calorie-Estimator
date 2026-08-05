
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from google import genai

import pandas as pd
import tempfile
import shutil
import os

from model.predict import predict_food

# =====================================================
# LOAD ENVIRONMENT VARIABLES
# =====================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in .env")

print("Loaded Key:", API_KEY[:10] + "...")

client = genai.Client(api_key=API_KEY)

# =====================================================
# TEST GEMINI CONNECTION
# =====================================================

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Say Hello"
    )
    print("Gemini Test:", response.text)

except Exception as e:
    print("\n========== GEMINI STARTUP ERROR ==========")
    print(type(e))
    print(e)
    print("==========================================\n")

# =====================================================
# FASTAPI APP
# =====================================================

app = FastAPI(
    title="AI Calorie Estimation API",
    version="2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# LOAD NUTRITION DATABASE
# =====================================================

CSV_PATH = "nutrition/nutrition_database.csv"

try:

    nutrition_df = pd.read_csv(CSV_PATH)
    nutrition_df["food"] = nutrition_df["food"].str.lower()

    print("Nutrition Records:", len(nutrition_df))

except Exception as e:

    print("Nutrition CSV Error:", e)

    nutrition_df = pd.DataFrame(columns=[
        "food",
        "calories",
        "protein",
        "carbs",
        "fat",
        "category"
    ])

# =====================================================
# GET NUTRITION
# =====================================================

def get_nutrition(food):

    row = nutrition_df[
        nutrition_df["food"] == food.lower()
    ]

    if row.empty:

        return {
            "calories": None,
            "protein": None,
            "carbs": None,
            "fat": None,
            "category": "Unknown"
        }

    row = row.iloc[0]

    return {
        "calories": int(row["calories"]),
        "protein": int(row["protein"]),
        "carbs": int(row["carbs"]),
        "fat": int(row["fat"]),
        "category": row["category"]
    }

# =====================================================
# HOME
# =====================================================

@app.get("/")
def home():

    return {
        "project": "AI Calorie Estimation",
        "status": "Running"
    }

# =====================================================
# HEALTH
# =====================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "model": "loaded",
        "nutrition_records": len(nutrition_df),
        "gemini": "configured"
    }

# =====================================================
# FOOD PREDICTION
# =====================================================

@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    temp_path = None

    try:

        suffix = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:

            shutil.copyfileobj(file.file, tmp)

            temp_path = tmp.name

        predictions = predict_food(temp_path)

        for item in predictions:

            nutrition = get_nutrition(item["food"])

            item.update(nutrition)

        return {
            "success": True,
            "predictions": predictions
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

# =====================================================
# GEMINI CHAT
# =====================================================

@app.post("/chat")
def chat(query: str):

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=query
        )

        return {
            "success": True,
            "response": response.text
        }

    except Exception as e:

        print("\n========== GEMINI ERROR ==========")
        print("Type :", type(e))
        print("Error:", repr(e))
        print("Text :", str(e))
        print("==================================")

        return {
            "success": False,
            "error": type(e).__name__,
            "details": str(e)
        }