from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime, timedelta
from places_utils import fetch_google_places, get_commute_time_minutes
from smart_filter import filter_places, inject_must_see_places

app = Flask(__name__)
CORS(app)

def format_time(minutes_after_8am):
    start = datetime.strptime("08:00", "%H:%M")
    return (start + timedelta(minutes=minutes_after_8am)).strftime("%I:%M %p")

@app.route("/plan", methods=["POST"])
def plan():
    try:
        data = request.get_json()
        city = data.get("city", "Cairo")
        days = int(data.get("days", 2))
        interests = data.get("interests", [])
        avoid_crowds = data.get("avoid_crowds", False)

        print(f"📍 {city} | Days: {days} | Interests: {interests} | Avoid Crowds: {avoid_crowds}")

        # Fetch & filter places
        places = fetch_google_places(city)
        must_see = inject_must_see_places(city)
        filtered = filter_places(places, interests, avoid_crowds)

        all_places = []
        seen = set()
        for p in must_see + filtered:
            name = p.get("name")
            if name and name not in seen:
                all_places.append(p)
                seen.add(name)

        if not all_places:
            return jsonify({"error": "No places found"}), 400

        # Fallback if too few places
        if len(all_places) < days * 3:
            all_places *= (days * 3) // len(all_places) + 1

        itinerary = []
        index = 0

        for d in range(days):
            time = 0  # in minutes after 8:00 AM
            plan = []
            last_place = None
            meals = {"lunch": False, "dinner": False}

            while index < len(all_places) and time < 600:  # 10 hours max
                place = all_places[index]
                commute = get_commute_time_minutes(last_place, place) if last_place else 0
                visit_time = 90  # default visit time
                total_time = commute + visit_time

                if time + total_time > 600:
                    break

                current_time = format_time(time + commute)
                name = place["name"]
                rating = place.get("rating", "?")
                address = place.get("formatted_address", "")
                tag = ""

                # Add a meal stop near lunch or dinner
                if not meals["lunch"] and (time + commute) >= 240:
                    tag = "🍽️ Lunch at "
                    meals["lunch"] = True
                elif not meals["dinner"] and (time + commute) >= 600:
                    tag = "🍽️ Dinner at "
                    meals["dinner"] = True
                elif "restaurant" in name.lower():
                    tag = "🍽️ Meal: "

                plan.append(f"{current_time}: {tag}{name} ({rating}★)\n  👉 {address}")
                time += total_time
                last_place = place
                index += 1

            itinerary.append(f"Day {d + 1}:\n" + "\n".join(plan))

        return jsonify({"itinerary": "\n\n".join(itinerary)})

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
