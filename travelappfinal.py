# travelappfinal.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from places_utils import fetch_google_places, get_commute_time_minutes
from smart_filter import filter_places, inject_must_see_places

app = Flask(__name__)
CORS(app)

@app.route("/plan", methods=["POST"])
def plan():
    try:
        data = request.get_json()
        city = data.get("city", "Cairo")
        days = int(data.get("days", 2))
        interests = data.get("interests", [])
        avoid_crowds = data.get("avoid_crowds", False)

        print(f"🌍 Received plan request for {city}, {days} day(s), interests: {interests}, avoid crowds: {avoid_crowds}")

        places = fetch_google_places(city)
        if not places:
            return jsonify({"error": "No places found"}), 400

        must_see = inject_must_see_places(city)
        filtered = filter_places(places, interests, avoid_crowds)

        # Combine and deduplicate
        seen = set()
        combined = []
        for place in must_see + filtered:
            name = place.get("name")
            if name not in seen:
                seen.add(name)
                combined.append(place)

        # Build day-by-day itinerary with commute awareness
        itinerary = []
        i = 0
        for day in range(days):
            day_plan = []
            time_left = 10 * 60  # 10 hours
            while i < len(combined) and time_left > 60:
                place = combined[i]
                visit_time = 90  # assume 1.5 hours per place
                commute = get_commute_time_minutes(
                    day_plan[-1] if day_plan else place, place)
                total = visit_time + commute
                if total <= time_left:
                    day_plan.append(place)
                    time_left -= total
                i += 1

            formatted = f"\nDay {day+1}:\n"
            for p in day_plan:
                formatted += f"- {p.get('name')} ({p.get('rating')}★)\n  👉 {p.get('formatted_address')}\n"
            itinerary.append(formatted.strip())

        return jsonify({"itinerary": "\n\n".join(itinerary)})

    except Exception as e:
        print("🔥 Error in /plan:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
