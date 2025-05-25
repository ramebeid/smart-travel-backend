import os
import openai
from places_utils import search_google_place

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_gpt_itinerary(city, days, interests, avoid_crowds):
    interest_text = ", ".join(interests) if interests else "general tourism"
    avoid_text = "Avoid crowded spots" if avoid_crowds else "Include popular sites"

    prompt = f"""
You are a smart local travel guide. Create a {days}-day hour-by-hour travel itinerary for a tourist visiting {city}. 

Make it highly personalized based on these interests: {interest_text}. {avoid_text}. 
Each day's plan should start at 10:00 and end around 18:30.

- Mention time before each entry (like “10:00 - Visit the Colosseum”)
- Include famous landmarks AND hidden gems.
- Recommend top local food stops (1 lunch + 1 café/snack per day)
- Assume all places are within reasonable distance and account for commute.
- Return the itinerary in plain text, organized by Day 1, Day 2, etc.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print("GPT error:", str(e))
        return None

def validate_itinerary_with_google(text, city):
    lines = text.strip().split("\n")
    validated = []

    for line in lines:
        if " - " in line:
            time_part, activity = line.split(" - ", 1)
            place_info = search_google_place(activity, city)

            if place_info:
                validated.append(f"{time_part} - {activity} ({place_info})")
            else:
                validated.append(f"{time_part} - {activity}")
        else:
            validated.append(line)

    return "\n".join(validated)
