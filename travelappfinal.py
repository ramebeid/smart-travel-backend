from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
from places_utils import fetch_google_places
from dotenv import load_dotenv
from smart_filter import filter_places, inject_must_see_places


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

@app.route("/plan", methods=["POST"])
def plan_trip():
    try:
        data = request.get_json()
        city = data.get("city", "")
        days = int(data.get("days", 1))
        interests = data.get("interests", [])
        avoid_crowds = data.get("avoid_crowds", False)

        places = fetch_google_places(city, GOOGLE_PLACES_API_KEY)
        smart_places = filter_places(places)
        smart_places = inject_must_see_places(city, smart_places)

        cleaned_places = list(set([p for p in places if len(p) > 10]))

        if not cleaned_places:
            cleaned_places = ["(no valid place data found — use local knowledge)"]

        # Strong GPT prompt with examples
        prompt = (
            f"You are a local expert planning a luxury hour-by-hour itinerary for a tourist visiting {city}.\n"
            f"The tourist is interested in: {', '.join(interests)} and will stay for {days} day(s).\n\n"
            f"Structure each day from 08:30 to 20:00 with:\n"
            f"- Excellent restaurants (must be ≥ 4.6★)\n"
            f"- Memorable experiences (hidden gems, cultural stops)\n"
            f"- Logical pathing (minimize commute time)\n"
            f"- Add transition notes like 'Walk 5 mins...' or 'Taxi 10 mins...'\n\n"
            f"Here are recommended locations from Google Places (name | rating | reviews | status | map link):\n\n"
            + "\n".join(cleaned_places[:15]) +
            f"\n\nUse these places when possible. Respond ONLY with the final itinerary in this format:\n\n"
            f"Day 1:\n08:30 - Breakfast at X (4.7★) - [map link]\n09:30 - Visit Museum Y...\n...\n"
        )

        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        itinerary = response.choices[0].message.content.strip()

        if not itinerary or len(itinerary.splitlines()) < 3:
            itinerary = (
                f"Sorry, we couldn’t generate a full itinerary for {city}.\n"
                f"Try different interests or refresh to regenerate.\n"
            )

        return jsonify({"itinerary": itinerary})

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
