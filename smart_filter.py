import os
from openai import OpenAI
from datetime import datetime, timedelta
from places_utils import get_place_details, get_commute_time_minutes

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_gpt_itinerary(city, days, interests, avoid_crowds):
    prompt = f"""
You are a local travel expert. Generate a detailed day-by-day itinerary for a visitor spending {days} day(s) in {city}. 
Their interests are: {', '.join(interests)}.
Make sure the itinerary:
- Starts at 10:00 AM and ends before 7:00 PM
- Includes realistic time slots for each location
- Accounts for commute time and time spent at each place
- Recommends top food spots, coffee shops, and hidden gems
- Avoids crowded areas if 'avoid crowds' is true
- Shows different recommendations each day

Respond in this JSON format:

{{
  "itinerary": [
    {{
      "day": 1,
      "entries": [
        {{
          "time": "10:00",
          "name": "Louvre Museum",
          "type": "museum",
          "notes": "Start your day with world-class art"
        }},
        ...
      ]
    }},
    ...
  ]
}}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    import json
    content = response.choices[0].message.content
    return json.loads(content).get("itinerary", [])

def validate_itinerary_with_google(raw_itinerary):
    validated = []
    for day_plan in raw_itinerary:
        day = day_plan["day"]
        entries = []

        for entry in day_plan["entries"]:
            details = get_place_details(entry["name"])
            if not details:
                continue

            rating = details.get("rating", 0)
            reviews = details.get("reviews", [])
            if rating < 4.6 or any(r.get("rating", 5) == 1 for r in reviews):
                continue

            commute = 15 if entries else 0
            entries.append({
                "day": day,
                "time": entry["time"],
                "name": entry["name"],
                "type": entry.get("type", ""),
                "notes": entry.get("notes", ""),
                "location": details.get("address", ""),
                "rating": rating,
                "commute_min": commute
            })

        if entries:
            validated.append({"day": day, "entries": entries})

    return validated
