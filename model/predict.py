import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import os

# ==========================================
# LOAD MODEL
# ==========================================

MODEL_PATH = os.path.join("model", "food_model.h5")

model = load_model(MODEL_PATH)

# ==========================================
# CLASS NAMES
# (Must match training order)
# ==========================================

class_names = [
    "biryani",
    "burger",
    "cake",
    "chapati",
    "chicken curry",
    "dal",
    "dosa",
    "french fries",
    "fried rice",
    "ice cream",
    "idli",
    "momos",
    "noodles",
    "paneer curry",
    "pasta",
    "pizza",
    "salad",
    "samosa",
    "sandwich",
    "upma"
]

# ==========================================
# PREDICTION FUNCTION
# ==========================================

def predict_food(img_path):
    """
    Predict the top 3 food classes from an image.

    Returns:
    [
        {
            "food": "pizza",
            "confidence": 98.45
        },
        ...
    ]
    """

    # Load image
    img = image.load_img(img_path, target_size=(224, 224))

    # Convert to array
    img_array = image.img_to_array(img)

    # Normalize
    img_array = img_array.astype("float32") / 255.0

    # Add batch dimension
    img_array = np.expand_dims(img_array, axis=0)

    # Predict
    predictions = model.predict(img_array, verbose=0)[0]

    # Top 3 predictions
    top_indices = predictions.argsort()[-3:][::-1]

    results = []

    for idx in top_indices:

        results.append(
            {
                "food": class_names[idx],
                "confidence": round(float(predictions[idx]) * 100, 2)
            }
        )

    return results