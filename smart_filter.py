import os
import openai
from places_utils import search_google_place, has_acceptable_reviews

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_gpt_itinerary(city, days, interests, avoid_crowds):
    interest_str = ", ".join(interests) if interests else "general tourism"
    prompt = f"""
You are a smart local guide. Create a {days}-day travel itinerary for {city} based on these interests: {interest_str}.
Make the plan realistic by considering distances and time spent at each location.
Avoid crowds if the user requests it: {'Yes' if avoid_crowds else 'No'}.
Include food stops (local cuisine) and cultural landmarks. Return only clean JSON like this:

[
  {{
    "name": "Eiffel Tower",
    "type": "landmark",
    "start_time": "10:00",
    "duration_min": 90,
    "location": "Champ de Mars, Paris"
  }},
  ...
]
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    content = response.choices[0].message.content.strip()
    try:
        return eval(content)  # assuming GPT returns a list of dicts
    except Exception as e:
        print("❌ GPT output error:", e)
        return []

def validate_itinerary_with_google(itinerary):
    valid = []
    for item in itinerary:
        place_data = search_google_place(item["name"])
        if place_data and has_acceptable_reviews(place_data):
            item["location"] = place_data.get("formatted_address", item.get("location", ""))
            item["cuisine"] = classify_cuisine(item["name"]) if "restaurant" in item.get("type", "") else ""
            valid.append(item)
    return valid

def classify_cuisine(name):
    prompt = f"What type of cuisine is served at '{name}'? Respond with a short phrase like 'Italian pizza' or 'Egyptian kebab'."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except:
        return ""
