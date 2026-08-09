import os
import tempfile
import shutil
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from groq import Groq

# ==============================
# BASE DIRECTORY
# ==============================

BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================
# ENVIRONMENT / GROQ CONFIG
# ==============================

load_dotenv()

GROQ_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_KEY:
    raise RuntimeError("GROQ_API_KEY is not configured")

client = Groq(api_key=GROQ_KEY)



GROQ_KEY = os.getenv("GROQ_API_KEY")


print("==============================")
print("GROQ KEY EXISTS:", bool(GROQ_KEY))
print("GROQ KEY START:", GROQ_KEY[:10] if GROQ_KEY else "NONE")
print("==============================")


if not GROQ_KEY:
    raise Exception("GROQ_API_KEY missing")


client = Groq(
    api_key=GROQ_KEY
)


# ==============================
# IMPORT MODEL
# ==============================

try:

    from model.predict import predict_food

    print("CNN Model Loaded")

except Exception as e:

    print("Model Import Error:",e)

    predict_food = None



# ==============================
# FASTAPI APP
# ==============================

app = FastAPI(
    title="AI Calorie Estimation API",
    version="2.0"
)



# CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# ==============================
# NUTRITION DATABASE
# ==============================


CSV_PATH = BASE_DIR / "nutrition" / "nutrition_database.csv"


try:

    nutrition_df = pd.read_csv(CSV_PATH)

    nutrition_df["food"] = (
        nutrition_df["food"]
        .astype(str)
        .str.lower()
    )


    print(
        "Nutrition Records:",
        len(nutrition_df)
    )


except Exception as e:

    print(
        "Nutrition CSV Error:",
        e
    )


    nutrition_df = pd.DataFrame()



# ==============================
# NUTRITION FUNCTION
# ==============================

def get_nutrition(food):

    if nutrition_df.empty:

        return {
            "calories":0,
            "protein":0,
            "carbs":0,
            "fat":0,
            "category":"Unknown"
        }


    row = nutrition_df[
        nutrition_df["food"] == food.lower()
    ]


    if row.empty:

        return {
            "calories":0,
            "protein":0,
            "carbs":0,
            "fat":0,
            "category":"Unknown"
        }


    row=row.iloc[0]


    return {
        "calories":int(row["calories"]),
        "protein":float(row["protein"]),
        "carbs":float(row["carbs"]),
        "fat":float(row["fat"]),
        "category":row["category"]
    }



# ==============================
# HOME
# ==============================


@app.get("/")
def home():

    return {

        "project":
        "AI Calorie Estimation",

        "status":
        "Running"

    }



# ==============================
# HEALTH
# ==============================


@app.get("/health")
def health():

    return {

        "status":"healthy",

        "model":
        "loaded",

        "nutrition_records":
        len(nutrition_df),

        "groq":
"configured" if client else "missing"

    }




# ==============================
# FOOD PREDICTION
# ==============================


@app.post("/predict")
async def predict(
    file:UploadFile=File(...)
):


    if predict_food is None:

        raise HTTPException(
            500,
            "CNN model not loaded"
        )


    temp_path=None


    try:


        suffix=os.path.splitext(
            file.filename
        )[1]


        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as tmp:


            shutil.copyfileobj(
                file.file,
                tmp
            )

            temp_path=tmp.name



        predictions=predict_food(
            temp_path
        )


        for item in predictions:

            nutrition=get_nutrition(
                item["food"]
            )


            item.update(
                nutrition
            )



        return {

            "success":True,

            "predictions":
            predictions

        }



    except Exception as e:


        raise HTTPException(
            500,
            str(e)
        )


    finally:


        if temp_path and os.path.exists(temp_path):

            os.remove(temp_path)




# ==============================
# GEMINI CHAT
# ==============================


@app.post("/chat")
def chat(query: str):

    try:

        response = client.chat.completions.create(

            model="llama-3.1-8b-instant",

            messages=[
                {
                    "role":"system",
                    "content":
                    """
                    You are an AI nutrition assistant.
                    Give healthy diet plans,
                    calorie advice and food suggestions.
                    """
                },
                {
                    "role":"user",
                    "content":query
                }
            ]
        )


        return {
            "success":True,
            "response":response.choices[0].message.content
        }


    except Exception as e:

        print("GROQ ERROR:",e)

        return {
            "success":False,
            "error":type(e).__name__,
            "details":str(e)
        }