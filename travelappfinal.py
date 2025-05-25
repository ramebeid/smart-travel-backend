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

        print(f"➡️  Generating GPT itinerary for {city}, {days}d, interests: {interests}")

        raw_itinerary = generate_gpt_itinerary(city, days, interests, avoid_crowds)
        final = validate_itinerary_with_google(raw_itinerary)

        if not final:
            return jsonify({"error": "Could not build itinerary"}), 500

        return jsonify({"itinerary": final})

    except Exception as e:
        print("❌ Error in /plan:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
