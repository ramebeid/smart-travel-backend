from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import timedelta, datetime
from places_utils import fetch_google_places, get_commute_time_minutes
from smart_filter import filter_places, inject_must_see_places

app = Flask(__name__)
CORS(app)

def format_time(minutes_since_8am):
    base = datetime.strptime("08:00", "%H:%M")
    new_time = base + timedelta(minutes=minutes_since_8am)
    return new_time.strftime("%I:%M %p")

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

        if len(all_places) < days * 3:
            all_places = all_places * ((days * 3) // len(all_places) + 1)

        itinerary = []
        i = 0

        for day in range(days):
            time_used = 0
            day_plan = []
            last_place = None
            meal_added = False

            while i < len(all_places) and time_used < 600:
                place = all_places[i]
                commute = get_commute_time_minutes(last_place, place) if last_place else 0
                visit_time = 90
                total_time = commute + visit_time

                if time_used + total_time > 600:
                    break

                current_time_label = format_time(time_used)
                stop_type = "Restaurant" if "restaurant" in place.get("name", "").lower() else "Visit"
                entry = f"{current_time_label}: {stop_type} {place['name']} ({place.get('rating', '?')}★)\n  👉 {place.get('formatted_address')}"

                if not meal_added and (time_used + commute) >= 240:
                    entry = f"{current_time_label}: Lunch break at {place['name']} ({place.get('rating', '?')}★)\n  👉 {place.get('formatted_address')}"
                    meal_added = True

                day_plan.append(entry)
                time_used += total_time
                last_place = place
                i += 1

            itinerary.append(f"Day {day + 1}:\n" + "\n".join(day_plan))

        return jsonify({"itinerary": "\n\n".join(itinerary)})

    except Exception as e:
        print("❌ ERROR in /plan:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
