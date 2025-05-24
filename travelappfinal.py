from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime, timedelta
from places_utils import fetch_google_places, get_commute_time_minutes
from smart_filter import filter_places, inject_must_see_places

app = Flask(__name__)
CORS(app)

def format_time(mins_after_8am):
    return (datetime.strptime("08:00", "%H:%M") + timedelta(minutes=mins_after_8am)).strftime("%I:%M %p")

@app.route("/plan", methods=["POST"])
def plan():
    try:
        data = request.get_json()
        city = data.get("city", "Cairo")
        days = int(data.get("days", 2))
        interests = data.get("interests", [])
        avoid_crowds = data.get("avoid_crowds", False)

        must_see = inject_must_see_places(city)
        extra = filter_places(fetch_google_places(city), interests, avoid_crowds)

        all_places = []
        seen = set()
        for p in must_see + extra:
            name = p["name"]
            if name not in seen:
                all_places.append(p)
                seen.add(name)

        if len(all_places) < days * 3:
            all_places *= (days * 3) // len(all_places) + 1

        itinerary = []
        i = 0

        for d in range(days):
            time = 0
            plan = []
            last = None
            meals = 0

            while i < len(all_places) and time < 600:
                p = all_places[i]
                commute = get_commute_time_minutes(last, p) if last else 0
                visit = 90
                block = commute + visit

                if time + block > 600:
                    break

                current = format_time(time + commute)
                label = p["name"]
                addr = p.get("formatted_address", "")
                rate = p.get("rating", "?")
                tag = ""

                if not meals and time >= 240:
                    tag = "🍽️ Lunch at "
                    meals += 1
                elif "restaurant" in label.lower() or "cafe" in label.lower():
                    tag = "🍽️ Eat at "

                plan.append(f"{current}: {tag}{label} ({rate}★)\n  👉 {addr}")
                time += block
                last = p
                i += 1

            itinerary.append(f"Day {d+1}:\n" + "\n".join(plan))

        return jsonify({"itinerary": "\n\n".join(itinerary)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
