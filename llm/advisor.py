def generate_advice(food, calories):

    if calories > 350:

        return f"{food} is a high calorie meal. Consider adding vegetables or reducing portion size."

    elif calories > 200:

        return f"{food} is a moderate calorie meal. Maintain balanced nutrition."

    else:

        return f"{food} is a low calorie meal. Good choice for a light diet."