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

        print(f"📍 Planning {days} days in {city} | Interests: {interests} | Avoid crowds: {avoid_crowds}")

        places = fetch_google_places(city)
        if not places:
            return jsonify({"error": "No places found"}), 400

        must_see = inject_must_see_places(city)
        good_places = filter_places(places, interests, avoid_crowds)

        all_places = []
        seen = set()
        for p in must_see + good_places:
            name = p.get("name")
            if name not in seen:
                all_places.append(p)
                seen.add(name)

        itinerary = []
        i = 0
        for day in range(days):
            day_plan = []
            time_left = 10 * 60
            while i < len(all_places) and time_left > 90:
                place = all_places[i]
                commute = get_commute_time_minutes(day_plan[-1] if day_plan else place, place)
                visit_time = 90
                total_time = visit_time + commute
                if total_time <= time_left:
                    day_plan.append(place)
                    time_left -= total_time
                i += 1

            formatted = f"Day {day+1}:\n"
            for p in day_plan:
                formatted += f"- {p['name']} ({p.get('rating', '?')}★)\n  👉 {p.get('formatted_address')}\n"
            itinerary.append(formatted.strip())

        return jsonify({"itinerary": "\n\n".join(itinerary)})
    except Exception as e:
        print("❌ ERROR in /plan:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
