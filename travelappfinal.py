import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from smart_filter import generate_gpt_itinerary, validate_itinerary_with_google

app = Flask(__name__)
CORS(app)

@app.route("/")
def health():
    return "Backend is alive"

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

        gpt_plan = generate_gpt_itinerary(city, days, interests, avoid_crowds)
        if not gpt_plan:
            return jsonify({"error": "GPT failed to return a plan"}), 500

        filtered = validate_itinerary_with_google(gpt_plan)
        if not filtered:
            return jsonify({"error": "All places filtered by Google"}), 404

        return jsonify({"itinerary": filtered})
    except Exception as e:
        print("❌ Exception in /plan:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
