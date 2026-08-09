import streamlit as st
import requests
from PIL import Image
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="AI Calorie Estimation",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CONFIG
# ==========================================

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000"
)
HISTORY_FILE = "history.json"

# ==========================================
# SESSION STATE
# ==========================================

if "prediction" not in st.session_state:
    st.session_state.prediction = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_saved" not in st.session_state:
    st.session_state.last_saved = None

if "quick_question" not in st.session_state:
    st.session_state.quick_question = ""

# ==========================================
# CUSTOM CSS
# ==========================================
st.markdown("""
<style>

.main {
    background-color: #f8fafc;
}

.main-title{
    text-align:center;
    font-size:45px;
    font-weight:bold;
    color:#ff4b4b;
}

.subtitle{
    text-align:center;
    color:#6c757d;
    font-size:18px;
    margin-bottom:25px;
}

.metric-card{
    background: linear-gradient(135deg,#ffffff,#f3f4f6);
    padding:20px;
    border-radius:18px;
    box-shadow:0px 4px 15px rgba(0,0,0,0.10);
    text-align:center;
    transition:0.3s;
}

.metric-card:hover{
    transform:scale(1.02);
}

.chart-card{
    background:white;
    padding:20px;
    border-radius:18px;
    box-shadow:0px 4px 15px rgba(0,0,0,0.08);
}

.stButton>button{
    width:100%;
    border-radius:12px;
    height:45px;
    font-size:17px;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# TITLE
# ==========================================

st.markdown(
    "<div class='main-title'>🍔 AI Calorie Estimation System</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='subtitle'>Deep Learning • FastAPI • TensorFlow • Gemini AI</div>",
    unsafe_allow_html=True
)

st.divider()
# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.image(
        "https://img.icons8.com/color/96/hamburger.png",
        width=80
    )

    st.title("AI Calorie Estimator")

    st.caption("Version 2.0")

    st.divider()

    page = st.radio(
        "📌 Navigation",
        [
            "🍔 Food Prediction",
            "🤖 AI Assistant",
            "📜 History",
            "📊 Dashboard",
            "🧮 BMI Calculator"
        ]
    )

    st.divider()

    st.subheader("⚡ Backend Status")

    try:

        response = requests.get(
            f"{API_URL}/health",
            timeout=5
        )

        if response.status_code == 200:

            data = response.json()

            st.success("🟢 Connected")

            st.write(f"**Model:** {data.get('model','Unknown')}")

            st.write(f"**Nutrition Records:** {data.get('nutrition_records',0)}")

            st.write(f"**Gemini:** {data.get('gemini','Unknown')}")

        else:

            st.error("Backend Error")

    except Exception:

        st.error("Backend Offline")

    st.divider()

    st.subheader("📊 Project")

    st.info(
        """
AI Calorie Estimation System

• TensorFlow CNN

• FastAPI Backend

• Streamlit Frontend

• Gemini AI Assistant

• Plotly Dashboard
        """
    )
# ==========================================
# HISTORY FUNCTIONS
# ==========================================

def load_history():

    if not os.path.exists(HISTORY_FILE):
        return []

    try:

        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)

        if not isinstance(history, list):
            return []

        return history

    except Exception:
        return []


def save_history(item):

    history = load_history()

    # Prevent duplicate consecutive entries
    if len(history) > 0:

        last = history[-1]

        if (
            last.get("food") == item.get("food")
            and last.get("confidence") == item.get("confidence")
        ):
            return

    history.append(item)

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

def generate_pdf(prediction):

    styles = getSampleStyleSheet()

    pdf = SimpleDocTemplate(
        "Nutrition_Report.pdf",
        pagesize=letter
    )

    story = []

    story.append(
        Paragraph(
            "<b>AI Calorie Estimation Report</b>",
            styles["Title"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Date:</b> {datetime.now()}",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph("<br/>", styles["Normal"])
    )

    story.append(
        Paragraph(
            f"<b>Food:</b> {prediction['food'].title()}",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Calories:</b> {prediction['calories']} kcal",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Protein:</b> {prediction['protein']} g",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Carbs:</b> {prediction['carbs']} g",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Fat:</b> {prediction['fat']} g",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Category:</b> {prediction['category']}",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Confidence:</b> {prediction['confidence']:.2f} %",
            styles["Normal"]
        )
    )

    pdf.build(story)

    return "Nutrition_Report.pdf"
def clear_history():

    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)


def history_dataframe():

    history = load_history()

    if len(history) == 0:
        return pd.DataFrame()

    df = pd.DataFrame(history)

    # Required columns
    required = [
        "date",
        "food",
        "calories",
        "protein",
        "carbs",
        "fat",
        "category",
        "confidence"
    ]

    for col in required:

        if col not in df.columns:

            if col in ["food", "category"]:
                df[col] = "Unknown"
            else:
                df[col] = 0

    df["food"] = df["food"].fillna("Unknown")
    df["category"] = df["category"].fillna("Unknown")

    numeric = [
        "calories",
        "protein",
        "carbs",
        "fat",
        "confidence"
    ]

    for col in numeric:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        ).fillna(0)

    return df
# ==========================================
# FOOD PREDICTION
# ==========================================

# ==========================================
# FOOD PREDICTION
# ==========================================

if page == "🍔 Food Prediction":

    st.header("🍔 AI Food Recognition")

    st.write(
        "Upload or capture a food image and let AI estimate calories and nutrition."
    )

    source = st.radio(
        "Select Image Source",
        [
            "📁 Upload Image",
            "📷 Camera"
        ],
        horizontal=True
    )

    uploaded_file = None

    if source == "📁 Upload Image":

        uploaded_file = st.file_uploader(
            "Upload Food Image",
            type=["jpg", "jpeg", "png"]
        )

    else:

        uploaded_file = st.camera_input(
            "Capture Food Image"
        )


    if uploaded_file:

        image = Image.open(uploaded_file)

        col1, col2 = st.columns(2)

        with col1:

            st.image(
                image,
                caption="Selected Image",
                use_container_width=True
            )


        with col2:

            st.subheader("🤖 AI Analysis")

            if st.button(
                "🚀 Predict Food",
                use_container_width=True
            ):

                with st.spinner("Analyzing image..."):

                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type
                        )
                    }

                    try:

                        response = requests.post(
                            f"{API_URL}/predict",
                            files=files,
                            timeout=120
                        )


                        if response.status_code == 200:

                            st.session_state.prediction = response.json()

                            st.success(
                                "Prediction Completed Successfully!"
                            )

                        else:

                            st.error(response.text)


                    except Exception as e:

                        st.error(str(e))


    # ==============================
    # SHOW RESULTS
    # ==============================

    if st.session_state.prediction:

        result = st.session_state.prediction


        if result.get("success"):

            st.divider()

            st.header("🍽 AI Prediction Results")


            predictions = result["predictions"]

            medals = [
                "🥇",
                "🥈",
                "🥉"
            ]


            for i, pred in enumerate(predictions):

                confidence = float(
                    pred.get("confidence",0)
                )

                with st.container(border=True):

                    st.subheader(
                        f"{medals[i]} {pred['food'].title()}"
                    )

                    st.progress(
                        min(confidence/100,1.0)
                    )

                    st.caption(
                        f"Confidence: {confidence:.2f}%"
                    )


                    c1,c2,c3,c4 = st.columns(4)


                    c1.metric(
                        "🔥 Calories",
                        f"{pred.get('calories',0)} kcal"
                    )


                    c2.metric(
                        "🥩 Protein",
                        f"{pred.get('protein',0)} g"
                    )


                    c3.metric(
                        "🍚 Carbs",
                        f"{pred.get('carbs',0)} g"
                    )


                    c4.metric(
                        "🧈 Fat",
                        f"{pred.get('fat',0)} g"
                    )


                    category = pred.get(
                        "category",
                        "Unknown"
                    )


                    if category == "Healthy":

                        st.success(
                            "🟢 Healthy Choice"
                        )

                    elif category == "Moderate":

                        st.warning(
                            "🟡 Moderate Calories"
                        )

                    else:

                        st.error(
                            "🔴 High Calorie Food"
                        )



            best = predictions[0]


            pdf_file = generate_pdf(best)


            with open(pdf_file,"rb") as pdf:

                st.download_button(
                    "📄 Download Nutrition Report",
                    pdf,
                    file_name="Nutrition_Report.pdf",
                    mime="application/pdf"
                )


            history_item = {

                "date":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M"
                ),

                "food":
                best.get("food","Unknown"),

                "calories":
                best.get("calories",0),

                "protein":
                best.get("protein",0),

                "carbs":
                best.get("carbs",0),

                "fat":
                best.get("fat",0),

                "category":
                best.get("category","Unknown"),

                "confidence":
                round(
                    float(
                        best.get("confidence",0)
                    ),
                    2
                )
            }


            save_history(history_item)



# ==========================================
# AI ASSISTANT
# ==========================================

elif page == "🤖 AI Assistant":

    st.header("🤖 AI Nutrition Assistant")

    st.write(
        "Ask anything about food, calories, diet, or healthy lifestyle."
    )


    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []


    # Display previous messages
    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.write(message["content"])



    question = st.chat_input(
        "Ask your nutrition question..."
    )


    if question:

        # Save user message
        st.session_state.messages.append(
            {
                "role":"user",
                "content":question
            }
        )


        with st.chat_message("user"):
            st.write(question)



        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                try:

                    response = requests.post(
                        f"{API_URL}/chat",
                        params={
                            "query": question
                        },
                        timeout=60
                    )


                    data = response.json()


                    if data.get("success"):

                        answer = data["response"]

                        st.write(answer)


                        # Save AI response
                        st.session_state.messages.append(
                            {
                                "role":"assistant",
                                "content":answer
                            }
                        )


                    else:

                        st.error(
                            data.get(
                                "details",
                                "Something went wrong"
                            )
                        )


                except Exception as e:

                    st.error(
                        f"Connection Error: {e}"
                    )


# ==========================================
# HISTORY
# ==========================================

elif page == "📜 History":

    st.header("📜 Prediction History")


    df = history_dataframe()


    if df.empty:

        st.info(
            "No prediction history available."
        )


    else:

        st.dataframe(
            df,
            use_container_width=True
        )


        st.download_button(
            "📥 Download History CSV",
            df.to_csv(index=False),
            "history.csv",
            "text/csv"
        )
# ==========================================
# DASHBOARD
# ==========================================

elif page == "📊 Dashboard":

    st.header("📊 AI Nutrition Dashboard")


    df = history_dataframe()


    if df.empty:

        st.info(
            "No prediction history available."
        )


    else:


        # ==============================
        # SUMMARY CARDS
        # ==============================

        total_predictions = len(df)

        avg_calories = round(
            df["calories"].mean(),
            1
        )

        avg_confidence = round(
            df["confidence"].mean(),
            1
        )

        healthy_count = len(
            df[
                df["category"] == "Healthy"
            ]
        )


        c1,c2,c3,c4 = st.columns(4)


        c1.metric(
            "🍽 Predictions",
            total_predictions
        )


        c2.metric(
            "🔥 Avg Calories",
            f"{avg_calories} kcal"
        )


        c3.metric(
            "🎯 Avg Confidence",
            f"{avg_confidence}%"
        )


        c4.metric(
            "🥗 Healthy Foods",
            healthy_count
        )


        st.divider()



        # ==============================
        # CALORIE CHART
        # ==============================

        st.subheader(
            "🔥 Calories by Food"
        )


        fig = px.bar(
            df,
            x="food",
            y="calories",
            color="food",
            text="calories",
            
            template="plotly_white"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )



        # ==============================
        # FOOD DISTRIBUTION
        # ==============================


        col1,col2 = st.columns(2)


        with col1:

            st.subheader(
                "🥧 Food Distribution"
            )


            pie = px.pie(
                df,
                names="food",
                hole=0.45
            )


            st.plotly_chart(
                pie,
                use_container_width=True
            )



        with col2:

            st.subheader(
                "🥗 Category Analysis"
            )


            category = px.pie(
                df,
                names="category",
                hole=0.45
            )


            st.plotly_chart(
                category,
                use_container_width=True
            )



        # ==============================
        # CONFIDENCE TREND
        # ==============================


        st.subheader(
            "📈 Confidence Trend"
        )


        line = px.line(
            df,
            x="date",
            y="confidence",
            markers=True,
            template="plotly_white"
        )


        st.plotly_chart(
            line,
            use_container_width=True
        )



        # ==============================
        # NUTRITION COMPARISON
        # ==============================


        st.subheader(
            "🍽 Nutrition Comparison"
        )


        nutrition = px.bar(
            df,
            x="food",
            y=[
                "protein",
                "carbs",
                "fat"
            ],
            barmode="group",
            template="plotly_white"
        )


        st.plotly_chart(
            nutrition,
            use_container_width=True
        )



        # ==============================
        # INSIGHTS
        # ==============================


        st.subheader(
            "📌 AI Insights"
        )


        highest_food = str(
            df.loc[
                df["calories"].idxmax(),
                "food"
            ]
        ).title()


        lowest_food = str(
            df.loc[
                df["calories"].idxmin(),
                "food"
            ]
        ).title()



        a,b,c = st.columns(3)


        with a:

            st.success(
                f"🔥 Highest Calorie\n\n{highest_food}"
            )


        with b:

            st.info(
                f"🥗 Lowest Calorie\n\n{lowest_food}"
            )


        with c:

            st.warning(
                f"🎯 Avg Confidence\n\n{avg_confidence}%"
            )



        st.divider()


        st.download_button(
            "📥 Download Dashboard Data",
            df.to_csv(index=False),
            "nutrition_report.csv",
            "text/csv"
        )
# ==========================================
# BMI CALCULATOR
# ==========================================

elif page == "🧮 BMI Calculator":

    st.header("🧮 Body Mass Index Calculator")

    st.write(
        "Calculate BMI and get basic health suggestions."
    )


    col1,col2 = st.columns(2)


    with col1:

        height = st.number_input(
            "Height (cm)",
            min_value=50,
            max_value=250,
            value=170
        )


    with col2:

        weight = st.number_input(
            "Weight (kg)",
            min_value=10,
            max_value=300,
            value=65
        )


    if st.button(
        "Calculate BMI",
        use_container_width=True
    ):


        bmi = weight / ((height/100)**2)


        st.metric(
            "Your BMI",
            f"{bmi:.2f}"
        )


        if bmi < 18.5:

            st.warning(
                "🟡 Underweight"
            )

            advice = """
Increase healthy calorie intake.

✅ Nuts  
✅ Milk  
✅ Eggs  
✅ Fruits
"""


        elif bmi < 25:

            st.success(
                "🟢 Normal Weight"
            )

            advice = """
Maintain your current lifestyle.

✅ Balanced diet  
✅ Exercise  
✅ Proper hydration
"""


        elif bmi < 30:

            st.warning(
                "🟠 Overweight"
            )

            advice = """
Focus on calorie control.

✅ More vegetables  
✅ Protein-rich foods  
✅ Regular walking
"""


        else:

            st.error(
                "🔴 Obese"
            )

            advice = """
Consider professional health guidance.

✅ Healthy eating  
✅ Regular exercise
"""


        st.subheader(
            "Personalized Advice"
        )

        st.info(advice)



# ==========================================
# DIET RECOMMENDATION
# ==========================================

elif page == "🍽 Diet Recommendation":

    st.header(
        "🍽 Personalized Diet Recommendation"
    )


    goal = st.selectbox(
        "Your Goal",
        [
            "Weight Loss",
            "Weight Gain",
            "Muscle Gain",
            "Maintain Weight"
        ]
    )


    meal = st.selectbox(
        "Meal Type",
        [
            "Breakfast",
            "Lunch",
            "Dinner",
            "Snacks"
        ]
    )


    recommendations = {


        "Weight Loss": {

            "Breakfast":
            [
                "Oats",
                "Idli + Sambar",
                "Fruit Bowl"
            ],

            "Lunch":
            [
                "Brown Rice + Dal",
                "Chapati + Vegetables"
            ],

            "Dinner":
            [
                "Vegetable Soup",
                "Paneer Salad"
            ],

            "Snacks":
            [
                "Apple",
                "Nuts"
            ]

        },


        "Weight Gain": {

            "Breakfast":
            [
                "Banana Shake",
                "Egg Omelette"
            ],

            "Lunch":
            [
                "Rice + Chicken Curry",
                "Paneer Rice"
            ],

            "Dinner":
            [
                "Chapati + Paneer"
            ],

            "Snacks":
            [
                "Dry Fruits",
                "Milk"
            ]

        },


        "Muscle Gain": {

            "Breakfast":
            [
                "Eggs",
                "Oats"
            ],

            "Lunch":
            [
                "Chicken Breast",
                "Brown Rice"
            ],

            "Dinner":
            [
                "Fish",
                "Chapati"
            ],

            "Snacks":
            [
                "Protein Shake",
                "Almonds"
            ]

        },


        "Maintain Weight": {

            "Breakfast":
            [
                "Idli",
                "Dosa",
                "Oats"
            ],

            "Lunch":
            [
                "Rice + Dal",
                "Chapati"
            ],

            "Dinner":
            [
                "Vegetables",
                "Soup"
            ],

            "Snacks":
            [
                "Fruits",
                "Curd"
            ]

        }

    }



    st.subheader(
        f"Recommended {meal}"
    )


    for food in recommendations[goal][meal]:

        st.success(food)



# ==========================================
# HOME PAGE
# ==========================================

elif page == "🏠 Home":

    st.title(
        "🍔 AI Calorie Estimation System"
    )


    st.markdown(
        """
## Your Personal AI Nutrition Assistant

Uses:

✅ Deep Learning  
✅ Computer Vision  
✅ FastAPI  
✅ Gemini AI  
✅ Data Visualization
"""
    )


    c1,c2,c3 = st.columns(3)


    with c1:

        st.info(
            """
### 🍔 Food Recognition

✔ CNN Model

✔ Calorie Prediction

✔ Nutrition Analysis
"""
        )


    with c2:

        st.success(
            """
### 🤖 AI Assistant

✔ Gemini AI

✔ Diet Suggestions

✔ Food Advice
"""
        )


    with c3:

        st.warning(
            """
### 📊 Analytics

✔ Dashboard

✔ History

✔ Reports
"""
        )


    st.divider()


    st.success(
        "🎉 Select a feature from sidebar to begin."
    )