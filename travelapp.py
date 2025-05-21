from flask import Flask, request, jsonify
import requests
import openai
import os
from dotenv import load_dotenv
from places_utils import fetch_google_places, fetch_eventbrite_events

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
EVENTBRITE_TOKEN = os.getenv("EVENTBRITE_TOKEN")

app = Flask(__name__)

@app.route("/plan", methods=["POST"])
def generate_plan():
    try:
        data = request.json
        city = data.get("city")
        days = int(data.get("days", 3))
        interests = data.get("interests", [])
        avoid_crowds = data.get("avoid_crowds", False)

        places = fetch_google_places(city, interests, GOOGLE_API_KEY)
        events = fetch_eventbrite_events(city, EVENTBRITE_TOKEN)

        avoid_text = "Avoid crowded times and tourist traps." if avoid_crowds else ""

        prompt = f'''You are a travel assistant helping users explore {city}.
The user wants a {days}-day plan.
Interests: {', '.join(interests)}.
{avoid_text}
Always include iconic historical sites, but avoid tourist trap restaurants and experiences.
Use only the places and events below:

Places:
{places}

Events:
{events}

Build a daily itinerary (morning, afternoon, evening) with names, descriptions, and links.
'''

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert travel itinerary assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        plan = response['choices'][0]['message']['content']
        return jsonify({"itinerary": plan})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
