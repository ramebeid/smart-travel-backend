import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from smart_filter import generate_gpt_itinerary, validate_itinerary_with_google

app = Flask(__name__)
CORS(app)

@app.route("/")
def health():
    return "Backend is running"

@app.route("/plan", methods=["POST"])
def plan():
    try:
        data = request.get_json()
        city = data.get("city")
        days = data.get("days", 1)
        interests = data.get("interests", [])
        avoid_crowds = data.get("avoid_crowds", False)

        if not city:
            return jsonify({"error": "Missing city"}), 400

        # STEP 1: Generate GPT-4 Itinerary
        raw_plan = generate_gpt_itinerary(city, days, interests, avoid_crowds)
        if not raw_plan:
            return jsonify({"error": "Failed to generate itinerary"}), 500

        # STEP 2: Validate / filter with Google
        enriched_plan = validate_itinerary_with_google(raw_plan, city)
        return jsonify({"itinerary": enriched_plan})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

